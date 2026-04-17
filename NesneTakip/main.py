import time
import ws_server
import tracker

def main():
    print("=" * 50)
    print("  Lazerle Nesne Takip Sistemi — YKİ Entegreli")
    print("  WebSocket : ws://localhost:8765")
    print("  Kontroller: q=çıkış  s=tarama  r=home")
    print("=" * 50)

    # WebSocket sunucusunu arka thread'de başlat
    ws_server.start()
    time.sleep(0.5)

    # Tracker ana thread'de çalışsın
    tracker.run()


if __name__ == "__main__":
    main()
