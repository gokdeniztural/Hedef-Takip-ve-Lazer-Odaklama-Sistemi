# paylaşılan veri

import threading
import time
import base64
import cv2
import config


class SharedState:
    def __init__(self):
        self._lock = threading.Lock()

        # Mod
        self.mode   = "SCAN"    # SCAN , TRACK
        self.locked = False     # hedef kilitli mi değil mi

        # Servo pozisyonları 
        self.pan_angle    = 90.0
        self.tilt_angle   = 90.0
        self.scan_direction = 1     
        self.last_scan_time = time.time()

        # PD kontrolcü geçmişi 
        self.prev_error_x = 0.0
        self.prev_error_y = 0.0

        #  Hedef kayıp sayacı 
        self.lost_counter = 0

        #  Thread-arası kuyruklar 
        self._command_queue: list[str] = []
        self._log_queue:     list[str] = []

        #  Yayınlanacak son frame
        self._latest_frame_b64: str | None = None

    # Komut kuyruğu

    def push_command(self, cmd: str) -> None:
        with self._lock:
            self._command_queue.append(cmd)

    def pop_commands(self) -> list[str]:
        with self._lock:
            cmds = list(self._command_queue)
            self._command_queue.clear()
            return cmds

    #  Log kuyruğu 

    def push_log(self, msg: str) -> None:
        with self._lock:
            self._log_queue.append(msg)
        print(f"[LOG] {msg}")

    def pop_logs(self) -> list[str]:
        with self._lock:
            logs = list(self._log_queue)
            self._log_queue.clear()
            return logs

    # Frame yönetimi

    def set_frame(self, frame_bgr) -> None:
        """BGR frame'i JPEG → base64 olarak sakla."""
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), config.STREAM_JPEG_QUALITY]
        _, buf = cv2.imencode(".jpg", frame_bgr, encode_param)
        b64 = base64.b64encode(buf).decode("utf-8")
        with self._lock:
            self._latest_frame_b64 = b64

    def get_frame(self) -> str | None:
        with self._lock:
            return self._latest_frame_b64

    # Durum özeti WebSocket'e gönderilecek kısım

    def get_status(self) -> dict:
        with self._lock:
            return {
                "mode":   self.mode,
                "locked": self.locked,
                "pan":    round(self.pan_angle, 1),
                "tilt":   round(self.tilt_angle, 1),
            }


# Tek örnek tüm modüller bunu import eder
shared = SharedState()
