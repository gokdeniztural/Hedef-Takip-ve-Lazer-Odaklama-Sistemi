"""
controller.py — Hareket kontrol modülü

Sorumluluklar:
  - PD kontrolcü (takip modu)
  - Tarama modu (180° süpürme)
  - YKİ komutlarını işleme (SCAN, TRACK, HOME, PAN:x, TILT:x)
"""

import time
import config
from state  import shared
from servo  import set_servo


#  TAKİP MODU — PD Kontrolcü
def update_tracking(cx: int, cy: int, W: int, H: int) -> None:
    """
    Hedef merkezi (cx, cy) ile frame merkezi arasındaki
    piksel hatasını servo açısına dönüştürür.

    PD formülü:  u = Kp * e  +  Kd * (e - e_prev)
      Kp terimi: hatanın büyüklüğüne orantılı düzeltme
      Kd terimi: hatanın değişim hızına orantılı frenleme
                 → servo hedefe yaklaşırken yavaşlar, sallanmaz

    Dead zone: ±DEAD_ZONE piksel içindeyse servo hareket etmez,
               böylece hedef merkezde titrememesi sağlanır.
    """
    err_x = cx - W // 2
    err_y = cy - H // 2

    if abs(err_x) < config.DEAD_ZONE:
        err_x = 0
    if abs(err_y) < config.DEAD_ZONE:
        err_y = 0

    if err_x == 0 and err_y == 0:
        return

    d_err_x = err_x - shared.prev_error_x
    d_err_y = err_y - shared.prev_error_y

    shared.pan_angle  += config.Kp * err_x + config.Kd * d_err_x
    shared.tilt_angle += config.Kp * err_y + config.Kd * d_err_y

    # Açıları fiziksel sınırlar içinde tut
    shared.pan_angle  = max(config.SCAN_MIN_ANGLE, min(config.SCAN_MAX_ANGLE, shared.pan_angle))
    shared.tilt_angle = max(0, min(180, shared.tilt_angle))

    shared.prev_error_x = err_x
    shared.prev_error_y = err_y

    set_servo(shared.pan_angle, shared.tilt_angle)



#  TARAMA MODU — 180° Scan


def update_scanning() -> None:
    # Pan servo'yu SCAN_MIN ↔ SCAN_MAX arasında ileri geri scan eder.
    now = time.time()
    if now - shared.last_scan_time < config.SCAN_SPEED:
        return

    shared.last_scan_time = now
    shared.pan_angle += config.SCAN_STEP * shared.scan_direction

    if shared.pan_angle >= config.SCAN_MAX_ANGLE:
        shared.pan_angle    = config.SCAN_MAX_ANGLE
        shared.scan_direction = -1
    elif shared.pan_angle <= config.SCAN_MIN_ANGLE:
        shared.pan_angle    = config.SCAN_MIN_ANGLE
        shared.scan_direction = 1

    set_servo(shared.pan_angle, shared.tilt_angle)


#  Yer Kontrol Sistem Komut İşleyici
def apply_command(cmd: str) -> None:
    """
    WebSocket üzerinden gelen YKİ komutunu uygular.

    Desteklenen komutlar:
      SCAN        → Tarama modunu zorla
      STOP_SCAN   → Taramayı durdur (TRACK'e geç)
      TRACK       → Takip modunu zorla
      STOP_TRACK  → Takibi durdur (SCAN'e geç)
      HOME        → Pan=90, Tilt=90 merkeze al
      PAN:<açı>   → Pan'ı belirtilen açıya götür (0-180)
      TILT:<açı>  → Tilt'i belirtilen açıya götür (0-180)
    """
    cmd = cmd.strip().upper()
    print(f"[CMD] {cmd}")

    if cmd == "SCAN":
        shared.mode = "SCAN"
        shared.push_log("Tarama modu aktif")

    elif cmd == "STOP_SCAN":
        shared.mode = "TRACK"
        shared.push_log("Tarama durduruldu")

    elif cmd == "TRACK":
        shared.mode = "TRACK"
        shared.push_log("Takip modu aktif")

    elif cmd == "STOP_TRACK":
        shared.mode   = "SCAN"
        shared.locked = False
        shared.push_log("Takip durduruldu → Tarama")

    elif cmd == "HOME":
        shared.pan_angle  = 90.0
        shared.tilt_angle = 90.0
        shared.locked     = False
        set_servo(90, 90)
        shared.push_log("HOME — Servo 90°/90°")

    elif cmd.startswith("PAN:"):
        try:
            angle = float(cmd.split(":")[1])
            shared.pan_angle = max(config.SCAN_MIN_ANGLE,
                                   min(config.SCAN_MAX_ANGLE, angle))
            set_servo(shared.pan_angle, shared.tilt_angle)
        except (ValueError, IndexError):
            shared.push_log(f"Geçersiz PAN komutu: {cmd}")

    elif cmd.startswith("TILT:"):
        try:
            angle = float(cmd.split(":")[1])
            shared.tilt_angle = max(0, min(180, angle))
            set_servo(shared.pan_angle, shared.tilt_angle)
        except (ValueError, IndexError):
            shared.push_log(f"Geçersiz TILT komutu: {cmd}")

    else:
        shared.push_log(f"Bilinmeyen komut: {cmd}")
