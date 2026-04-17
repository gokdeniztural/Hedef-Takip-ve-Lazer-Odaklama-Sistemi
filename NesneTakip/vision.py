#vision.py — Görüntü işleme modülü
import cv2
import numpy as np
import time
import config
from state import shared

# FPS hesabı için
_prev_time = time.time()

#  MASKE & HEDEF TESPİTİ
def preprocess(frame) -> np.ndarray:
    hsv  = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, config.LOWER_HSV, config.UPPER_HSV)
    kernel = np.ones(
        (config.MORPH_KERNEL_SIZE, config.MORPH_KERNEL_SIZE), np.uint8
    )
    mask = cv2.erode(mask,  kernel, iterations=config.MORPH_ITERATIONS)
    mask = cv2.dilate(mask, kernel, iterations=config.MORPH_ITERATIONS)
    return mask


def find_largest_target(mask: np.ndarray):
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    if not contours:
        return None

    largest = max(contours, key=cv2.contourArea)
    area    = cv2.contourArea(largest)

    if area < config.MIN_CONTOUR_AREA:
        return None

    M = cv2.moments(largest)
    if M["m00"] == 0:
        return None

    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])

    return cx, cy, area, largest

#  HUD ÇİZİMİ

def draw_overlay(frame, mask, target, W: int, H: int):
    global _prev_time

    cx_frame = W // 2
    cy_frame = H // 2

    # Izgara
    for x in range(0, W, 80):
        cv2.line(frame, (x, 0), (x, H), (20, 40, 20), 1)
    for y in range(0, H, 80):
        cv2.line(frame, (0, y), (W, y), (20, 40, 20), 1)

    # Crosshair
    cv2.line(frame,   (cx_frame - 30, cy_frame), (cx_frame + 30, cy_frame), (0, 255, 100), 1)
    cv2.line(frame,   (cx_frame, cy_frame - 30), (cx_frame, cy_frame + 30), (0, 255, 100), 1)
    cv2.circle(frame, (cx_frame, cy_frame), config.DEAD_ZONE, (0, 255, 100), 1)

    # Hedef varsa çiz
    if target:
        tcx, tcy, area, contour = target

        # Bounding box
        bx, by, bw, bh = cv2.boundingRect(contour)
        cv2.rectangle(frame, (bx, by), (bx + bw, by + bh), (0, 0, 255), 2)

        # Köşe L-işaretleri
        clen = 14
        ccol = (0, 0, 255)
        # Sol üst
        cv2.line(frame, (bx,      by),      (bx + clen, by),           ccol, 2)
        cv2.line(frame, (bx,      by),      (bx,        by + clen),    ccol, 2)
        # Sağ üst
        cv2.line(frame, (bx + bw, by),      (bx + bw - clen, by),      ccol, 2)
        cv2.line(frame, (bx + bw, by),      (bx + bw,  by + clen),     ccol, 2)
        # Sol alt
        cv2.line(frame, (bx,      by + bh), (bx + clen, by + bh),      ccol, 2)
        cv2.line(frame, (bx,      by + bh), (bx,        by + bh - clen), ccol, 2)
        # Sağ alt
        cv2.line(frame, (bx + bw, by + bh), (bx + bw - clen, by + bh),      ccol, 2)
        cv2.line(frame, (bx + bw, by + bh), (bx + bw,  by + bh - clen),     ccol, 2)

        # Hedef merkezi
        cv2.circle(frame, (tcx, tcy), 5, (0, 0, 255), -1)

        # Merkez → hedef hata vektörü
        cv2.line(frame, (cx_frame, cy_frame), (tcx, tcy), (0, 0, 255), 1)

        # Etiket
        cv2.putText(
            frame, f"LOCKED ({tcx},{tcy})",
            (bx, by - 8),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2
        )

    # HUD bilgisi
    status = shared.get_status()
    mode_color = (0, 255, 100) if status["mode"] == "TRACK" else (0, 165, 255)
    cv2.putText(frame, f'MOD: {status["mode"]}',
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, mode_color, 2)
    cv2.putText(frame, f'PAN:{status["pan"]:.0f}  TILT:{status["tilt"]:.0f}',
                (10, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

    # FPS göstergesi
    now  = time.time()
    fps  = 1.0 / (now - _prev_time + 1e-9)
    _prev_time = now
    fps_color = (0, 255, 100) if fps >= 20 else (0, 165, 255) if fps >= 10 else (0, 0, 255)
    cv2.putText(frame, f'FPS: {fps:.0f}',
                (10, 82), cv2.FONT_HERSHEY_SIMPLEX, 0.55, fps_color, 1)

    # Mini maskeleme göstergesi
    mask_small = cv2.resize(mask, (160, 120))
    mask_bgr   = cv2.cvtColor(mask_small, cv2.COLOR_GRAY2BGR)
    frame[10:130, W - 170:W - 10] = mask_bgr
    cv2.putText(frame, "MASKE",
                (W - 168, 148), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 100, 100), 1)

    return frame