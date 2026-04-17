import asyncio
import json
import threading
import websockets
import websockets.exceptions

import config
from state import shared


# Bağlı tüm istemciler (broadcast için)
_clients: set = set()


async def _handler(websocket) -> None:
    #Her bağlanan YKİ istemcisi için çalışır.
    addr = websocket.remote_address
    print(f"[WS] Bağlandı: {addr}")
    shared.push_log(f"YKİ bağlandı: {addr[0]}")
    _clients.add(websocket)

    try:
        async for raw in websocket:
            try:
                data = json.loads(raw)
                cmd  = data.get("command", "").strip()
            except json.JSONDecodeError:
                cmd = raw.strip()

            if cmd:
                shared.push_command(cmd)

    except websockets.exceptions.ConnectionClosedError:
        pass
    finally:
        _clients.discard(websocket)
        print(f"[WS] Kesildi: {addr}")


async def _broadcast_loop() -> None:
    interval = 1.0 / config.STREAM_FPS

    while True:
        await asyncio.sleep(interval)

        # Snapshot al — set'i döngü sırasında değiştirmemek için
        active = list(_clients)
        if not active:
            continue

        frame_b64 = shared.get_frame()
        if frame_b64 is None:
            continue

        status = shared.get_status()
        logs   = shared.pop_logs()

        payload = json.dumps({
            "frame":  frame_b64,
            "pan":    status["pan"],
            "tilt":   status["tilt"],
            "mode":   status["mode"],
            "locked": status["locked"],
        })

        for client in active:
            try:
                await client.send(payload)
                for msg in logs:
                    await client.send(json.dumps({"log": msg}))
            except Exception:
                _clients.discard(client)


async def _main() -> None:
    print(f"[WS] Sunucu başladı → ws://{config.WS_HOST}:{config.WS_PORT}")
    async with websockets.serve(_handler, config.WS_HOST, config.WS_PORT):
        await _broadcast_loop()


def start() -> None:
    """WebSocket sunucusunu ayrı thread'de başlat (ana thread'i bloklamaz)."""
    def _run():
        asyncio.run(_main())

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return t