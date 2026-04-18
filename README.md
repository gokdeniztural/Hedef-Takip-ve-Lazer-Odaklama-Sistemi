# 🎯 NesneTakip — Gerçek Zamanlı Nesne Takip Sistemi

> HSV renk tespiti, PD kontrol ve WebSocket tabanlı yer kontrol istasyonu ile donatılmış pan-tilt servo takip sistemi.
> (Bu proje Bilgisayar Organizasyonu dersi kapsamında final projesi olarak ekip arkadaşlarım ile birlikte hazırlanmıştır!)

---

## 📸 Sistem Önizlemesi

| Bileşen | Açıklama |
|---------|----------|
| **Tracker** | OpenCV ile HSV renk maskesi, kontur tespiti ve PD kontrolcü |
| **Servo Sürücüsü** | Raspberry Pi GPIO/PWM (PC'de simülasyon modu) |
| **WebSocket Sunucusu** | Canlı video akışı + komut alımı (asyncio + websockets) |
| **YKİ Arayüzü** | Tarayıcı tabanlı yer kontrol istasyonu (saf HTML/JS) |

---

## 🗂️ Proje Yapısı

```
NESNETAKIP/
├── NesneTakip/
│   ├── config.py              # Tüm ayarlar tek dosyada
│   ├── controller.py          # PD kontrolcü, tarama modu, YKİ komut işleyici
│   ├── hsv_finder.py          # HSV aralığı ayarlama aracı (trackbar GUI)
│   ├── main.py                # Giriş noktası — WS sunucusu + tracker'ı başlatır
│   ├── servo.py               # GPIO/PWM sürücüsü (Pi) veya stub (PC)
│   ├── state.py               # Thread-safe paylaşılan durum (SharedState)
│   ├── tracker.py             # Ana döngü: kamera → işleme → servo → stream
│   ├── vision.py              # Görüntü işleme: HSV maskesi, kontur tespiti, HUD
│   └── ws_server.py           # asyncio WebSocket sunucusu + broadcast döngüsü
├── venv/                      # Python sanal ortamı (git'e dahil değil)
├── YerKontrolSistemi/
│   └── yki2_updated.html      # Tarayıcı tabanlı yer kontrol arayüzü
├── .gitignore
└── requirements.txt           # Python bağımlılıkları
```

---

## ⚙️ Kurulum

### Gereksinimler

- Python 3.11+
- OpenCV
- websockets
- numpy
- RPi.GPIO *(yalnızca Raspberry Pi için)*

### Sanal Ortam Oluştur

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# kaynak venv/bin/activate   # Linux / macOS
```

### Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

> Raspberry Pi üzerinde çalışıyorsanız ek olarak:
> ```bash
> pip install RPi.GPIO
> ```

---

## 🚀 Çalıştırma

```bash
python NesneTakip/main.py
```

Ardından `YerKontrolSistemi/yki2_updated.html` dosyasını tarayıcıda açın ve `ws://localhost:8765` adresine bağlanın.

---

## 🎨 HSV Renk Aralığı Ayarlama

Takip edilecek nesnenin rengini bulmak için:

```bash
python NesneTakip/hsv_finder.py
```

Trackbar'ları ayarlayarak nesneyi beyaz maskeyle eşleştirin. Çıkışta görünen değerleri `config.py` dosyasına yapıştırın:

```python
LOWER_HSV = np.array([H_min, S_min, V_min])
UPPER_HSV = np.array([H_max, S_max, V_max])
```

---

## 🖥️ YKİ — Yer Kontrol İstasyonu

Tarayıcı tabanlı arayüz şu özellikleri sunar:

- **SCAN** — Pan servosunu 0°–180° arasında süpürür
- **TRACK** — Tespit edilen hedefe kilitlenir
- **HOME** — Servoları 90°/90° merkeze alır
- **PAN / TILT sliders** — Manuel servo kontrolü
- Canlı video akışı (Base64 JPEG over WebSocket)
- Gerçek zamanlı log paneli

---

## 🔧 Konfigürasyon (`config.py`)

| Parametre | Varsayılan | Açıklama |
|-----------|-----------|----------|
| `CAMERA_INDEX` | `0` | Kamera indeksi |
| `FRAME_WIDTH / HEIGHT` | `640 × 480` | Çözünürlük |
| `LOWER_HSV / UPPER_HSV` | Kırmızı ton | HSV renk aralığı |
| `MIN_CONTOUR_AREA` | `500 px²` | Gürültü filtresi |
| `DEAD_ZONE` | `15 px` | Servo titreme engeli |
| `LOST_THRESHOLD` | `30 frame` | Hedef kayıp → tarama gecikmesi |
| `Kp / Kd` | `0.05 / 0.01` | PD kontrolcü katsayıları |
| `SCAN_STEP / SPEED` | `2° / 0.05s` | Tarama hızı |
| `SERVO_ENABLED` | `False` | Pi'de `True` yapın |
| `WS_PORT` | `8765` | WebSocket portu |
| `STREAM_FPS` | `30` | Yayın hedef FPS |

---

## 🤖 Desteklenen YKİ Komutları

| Komut | Açıklama |
|-------|----------|
| `SCAN` | Tarama modunu başlat |
| `STOP_SCAN` | Taramayı durdur |
| `TRACK` | Takip modunu zorla |
| `STOP_TRACK` | Takibi durdur → taramaya geç |
| `HOME` | Servoları merkeze al (90°/90°) |
| `PAN:<açı>` | Pan'ı belirtilen açıya götür (0–180) |
| `TILT:<açı>` | Tilt'i belirtilen açıya götür (0–180) |

---

## 🔌 Donanım (Raspberry Pi)

| Bileşen | Bağlantı |
|---------|----------|
| Pan Servo | GPIO BCM 17 |
| Tilt Servo | GPIO BCM 18 |
| Servo Modeli | SG90 (PWM 50 Hz) |

`config.py` içinde `SERVO_ENABLED = True` yaparak GPIO'yu etkinleştirin.

---

## 🏗️ Mimari

```
┌─────────────┐     frame      ┌──────────────┐
│  tracker.py │ ─────────────► │   vision.py  │  HSV + kontur
│  (ana döngü)│ ◄───────────── │              │  tespiti
└──────┬──────┘    target      └──────────────┘
       │
       │ servo açıları
       ▼
┌──────────────┐              ┌──────────────┐
│ controller.py│ ────────────►│   servo.py   │  GPIO/PWM
│ PD + tarama  │              │              │  (veya stub)
└──────────────┘              └──────────────┘
       │
       │ SharedState (thread-safe)
       ▼
┌──────────────┐   WebSocket   ┌──────────────┐
│  ws_server.py│ ◄────────────►│  YKİ (HTML)  │  Tarayıcı
│  broadcast   │   komut/frame │              │  arayüzü
└──────────────┘               └──────────────┘
```

---

## 📄 Lisans

Bu proje eğitim ve kişisel kullanım amaçlıdır.

---

*Geliştirici notu: PC'de test ederken `SERVO_ENABLED = False` bırakın. Servo komutları yalnızca loglanır, GPIO'ya dokunulmaz.*
