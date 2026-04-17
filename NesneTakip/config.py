# Proje genelindeki tüm ayarlar

import numpy as np

#  KAMERA
CAMERA_INDEX  = 0
FRAME_WIDTH   = 640
FRAME_HEIGHT  = 480

#  HSV RENK ARALIĞI (hsv_finder.py ile bul)
LOWER_HSV = np.array([145, 111, 95])
UPPER_HSV = np.array([179, 255, 156])


#  GÖRÜNTÜ İŞLEME
MIN_CONTOUR_AREA  = 500     # piksel²  küçük gürültüleri eliyor
MORPH_KERNEL_SIZE = 5       # morfoloji kernel boyutu
MORPH_ITERATIONS  = 2       # erode/dilate tekrar sayısı


#  TAKİP / KONTROL
DEAD_ZONE      = 15    # piksel bu alan içinde servo hareket etmez
LOST_THRESHOLD = 30    # kaç frame sonra tarama moduna geçilir

# PD kontrolcü katsayıları
Kp = 0.05   # büyüttüğümğzde hızlı tepki alsak da sallanmaya yol açtı!
Kd = 0.01   # türev — aşımı (overshoot) azaltır

#  TARAMA MODU
SCAN_STEP      = 2      # derece / adım
SCAN_SPEED     = 0.05   # saniye / adım
SCAN_MIN_ANGLE = 0      # pan minimum
SCAN_MAX_ANGLE = 180    # pan maksimum


#  SERVO (Raspberry Pi)
SERVO_ENABLED = False   # Pi'de True yap --> Pc için False kalmalı gerek yok!
PAN_PIN       = 17      # GPIO BCM pin numarası
TILT_PIN      = 18

# SG90 için duty cycle hesabı
SERVO_DUTY_MIN = 2.5
SERVO_DUTY_MAX = 12.5
SERVO_PWM_FREQ = 50     # Hz

#  WEBSOCKET SUNUCUSU
WS_HOST           = "0.0.0.0"
WS_PORT           = 8765
STREAM_FPS        = 30          # broadcast hedef FPS
STREAM_JPEG_QUALITY = 60        # 0-100
