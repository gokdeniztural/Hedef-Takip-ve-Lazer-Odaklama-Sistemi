"""
tracker.py — Ana tracker döngüsü

Görüntü işleme  → vision.py
Servo/kontrol   → controller.py
Paylaşılan veri → state.py
Servo sürücüsü  → servo.py
"""

import cv2
import time

import config
from state      import shared
from vision     import preprocess, find_largest_target, draw_overlay
from controller import update_tracking, update_scanning, apply_command
from servo      import cleanup as servo_cleanup


def run() -> None:
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    if not cap.isOpened():
        print("[HATA] Kamera açılamadı!")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[TRACKER] Çözünürlük: {W}x{H}")
    print("[TRACKER] Kontroller: q=çıkış  s=tarama  r=home")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[HATA] Frame alınamadı")
            break

        #YKİ komutlarını uygula 
        for cmd in shared.pop_commands():
            apply_command(cmd)

        # Görüntü işleme
        mask   = preprocess(frame)
        target = find_largest_target(mask)

        #Durum makinesi
        if target:
            shared.lost_counter = 0
            shared.locked       = True

            if shared.mode == "SCAN":
                # Tarama sırasında hedef bulununca otomatik kilitle
                shared.mode = "TRACK"
                shared.push_log("Hedef tespit edildi → Takip başladı")

            cx, cy, *_ = target
            update_tracking(cx, cy, W, H)

        else:
            shared.locked       = False
            shared.lost_counter += 1

            if shared.lost_counter >= config.LOST_THRESHOLD:
                if shared.mode == "TRACK":
                    shared.mode = "SCAN"
                    shared.push_log("Hedef kayboldu → Tarama başladı")

            update_scanning()

        # HUD çiz ve stream'e ver
        frame = draw_overlay(frame, mask, target, W, H)
        shared.set_frame(frame)

        # Yerel pencere
        cv2.imshow("Tracker", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break
        elif key == ord("s"):
            shared.mode         = "SCAN"
            shared.lost_counter = config.LOST_THRESHOLD
        elif key == ord("r"):
            apply_command("HOME")

    # Temizlik
    cap.release()
    cv2.destroyAllWindows()
    servo_cleanup()
