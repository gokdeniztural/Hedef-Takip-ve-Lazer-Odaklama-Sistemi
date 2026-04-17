"""
HSV Renk Aralığı Bulucu
-----------------------
Takip etmek istediğin nesnenin doğru HSV aralığını bulmak için
bu aracı çalıştır. Trackbar'ları ayarlayarak maskeyi canlı gör.

Kullanım: python hsv_finder.py
Çıkış: q tuşu
"""

import cv2
import numpy as np


def nothing(x):
    pass


cap = cv2.VideoCapture(0)

cv2.namedWindow("HSV Ayarlayici")

# H: 0-179, S: 0-255, V: 0-255 (OpenCV HSV aralığı)
cv2.createTrackbar("H_min", "HSV Ayarlayici", 0,   179, nothing)
cv2.createTrackbar("H_max", "HSV Ayarlayici", 179, 179, nothing)
cv2.createTrackbar("S_min", "HSV Ayarlayici", 100, 255, nothing)
cv2.createTrackbar("S_max", "HSV Ayarlayici", 255, 255, nothing)
cv2.createTrackbar("V_min", "HSV Ayarlayici", 100, 255, nothing)
cv2.createTrackbar("V_max", "HSV Ayarlayici", 255, 255, nothing)

print("[BİLGİ] Trackbar'ları ayarla, nesnen beyaza dönünce değerleri not al.")
print("[BİLGİ] Çıkış için 'q' tuşuna bas.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    h_min = cv2.getTrackbarPos("H_min", "HSV Ayarlayici")
    h_max = cv2.getTrackbarPos("H_max", "HSV Ayarlayici")
    s_min = cv2.getTrackbarPos("S_min", "HSV Ayarlayici")
    s_max = cv2.getTrackbarPos("S_max", "HSV Ayarlayici")
    v_min = cv2.getTrackbarPos("V_min", "HSV Ayarlayici")
    v_max = cv2.getTrackbarPos("V_max", "HSV Ayarlayici")

    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])

    mask = cv2.inRange(hsv, lower, upper)

    # Maskeli görüntü
    result = cv2.bitwise_and(frame, frame, mask=mask)

    # Değerleri ekrana yaz
    info = f"HSV: [{h_min},{s_min},{v_min}] - [{h_max},{s_max},{v_max}]"
    cv2.putText(frame, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow("Orijinal", frame)
    cv2.imshow("Maske (Beyaz = Hedef)", mask)
    cv2.imshow("Maskelenmis Goruntu", result)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        print(f"\n[SONUC] Kopyala ve tracker.py'ye yapistir:")
        print(f"  LOWER_HSV = np.array([{h_min}, {s_min}, {v_min}])")
        print(f"  UPPER_HSV = np.array([{h_max}, {s_max}, {v_max}])")
        break

cap.release()
cv2.destroyAllWindows()
