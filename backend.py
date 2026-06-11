import asyncio
import json
import socket
import threading
import time
import random
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import uvicorn

try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP, ARP, Ether
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

# ── Detect local IPs at startup ───────────────────────────────────────────────
def _detect_local_ips():
    ips = {'127.0.0.1', 'localhost', '::1'}
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ips.add(s.getsockname()[0])
        s.close()
    except Exception:
        pass
    try:
        import subprocess
        out = subprocess.run(['hostname', '-I'], capture_output=True, text=True, timeout=2).stdout
        for ip in out.split():
            ips.add(ip.strip())
    except Exception:
        pass
    return ips

LOCAL_IPS = _detect_local_ips()
print(f"[backend] IPs locales detectadas: {LOCAL_IPS}")

# ── Identificación de servicios por prefijo IP ────────────────────────────────
_SERVICE_PREFIXES = [
    ("Google",     ["8.8.8.", "8.8.4.", "142.250.", "142.251.", "172.217.", "216.58.", "74.125.", "64.233.", "34.64.", "34.96.", "34.102.", "34.104."]),
    ("Netflix",    ["198.38.", "208.75.", "23.246.", "37.77.", "45.57.", "108.175."]),
    ("Cloudflare", ["1.1.1.", "1.0.0.", "104.16.", "104.17.", "104.18.", "104.19.", "104.20.", "104.21."]),
    ("AWS",        ["54.230.", "52.92.", "52.94.", "18.212.", "18.213.", "34.195.", "52.84."]),
    ("Meta",       ["157.240.", "179.60.", "31.13.", "163.70.", "185.89.", "129.134."]),
    ("Microsoft",  ["13.64.", "13.65.", "13.66.", "13.107.", "40.76.", "40.112.", "52.96.", "20.42."]),
    ("Apple",      ["17.172.", "17.57.", "17.253.", "17.142."]),
    ("GitHub",     ["140.82.", "192.30.", "185.199."]),
    ("Akamai",     ["23.0.", "23.1.", "23.2.", "23.3.", "184.24.", "184.25."]),
    ("Spotify",    ["35.186.", "78.31.", "35.166."]),
    ("Discord",    ["66.22.", "162.159."]),
]

def identify_service(ip):
    for name, prefixes in _SERVICE_PREFIXES:
        for p in prefixes:
            if ip.startswith(p):
                return name
    return None

_demo_mode = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global packet_queue, _loop, _demo_mode
    packet_queue = asyncio.Queue(maxsize=500)
    _loop = asyncio.get_event_loop()
    asyncio.create_task(broadcast_packets())

    if SCAPY_AVAILABLE:
        def sniffer():
            try:
                sniff(prn=packet_callback, store=False)
            except Exception as e:
                print(f"[sniffer] sin permisos ({e})")
                print("[backend] ejecutar con sudo para captura real — activando modo demo")
                asyncio.run_coroutine_threadsafe(_start_demo(), _loop)
        threading.Thread(target=sniffer, daemon=True).start()
        print("[backend] scapy iniciado — esperando permisos...")
    else:
        asyncio.create_task(_start_demo())
        print("[backend] scapy no disponible — modo demo")

    yield


async def _start_demo():
    global _demo_mode
    _demo_mode = True
    print("[backend] modo demo activo")
    await demo_generator()


app = FastAPI(lifespan=lifespan)

clients = []
packet_queue = None
_loop = None

PROTOCOL_MAP = {
    "TCP":   {"type": "sedan",  "color": 0x3B82F6, "speed": 1.0, "lane": 0},
    "UDP":   {"type": "sports", "color": 0xF59E0B, "speed": 1.6, "lane": 1},
    "ICMP":  {"type": "moto",   "color": 0xEF4444, "speed": 2.0, "lane": 0},
    "DNS":   {"type": "taxi",   "color": 0xFBBF24, "speed": 1.2, "lane": 0},
    "HTTP":  {"type": "truck",  "color": 0x10B981, "speed": 0.7, "lane": 1},
    "HTTPS": {"type": "truck",  "color": 0x6366F1, "speed": 0.7,  "lane": 1},
    "SSH":   {"type": "sports", "color": 0x14B8A6, "speed": 1.4,  "lane": 0},
    "DHCP":  {"type": "van",    "color": 0xF472B6, "speed": 0.8,  "lane": 1},
    "ARP":   {"type": "van",    "color": 0x8B5CF6, "speed": 0.9,  "lane": 1},
    "OTHER": {"type": "sedan",  "color": 0x6B7280, "speed": 1.0, "lane": 0},
}

_packet_id = 0


def _direction(src, dst):
    if src in LOCAL_IPS:
        return "out"
    if dst in LOCAL_IPS:
        return "in"
    return "out"


def classify_packet(pkt):
    global _packet_id
    _packet_id += 1

    proto = "OTHER"
    src = "?"
    dst = "?"
    size = len(pkt)
    info = ""
    sport = 0
    tcp_flags = "—"
    mac_src = pkt[Ether].src if Ether in pkt else "N/D"
    mac_dst = pkt[Ether].dst if Ether in pkt else "N/D"

    if IP in pkt:
        src = pkt[IP].src
        dst = pkt[IP].dst

        if TCP in pkt:
            dport = pkt[TCP].dport
            sport = pkt[TCP].sport
            if dport == 443 or sport == 443:
                proto = "HTTPS"
            elif dport == 80 or sport == 80:
                proto = "HTTP"
            elif dport == 22 or sport == 22:
                proto = "SSH"
            else:
                proto = "TCP"
            info = f":{dport}"
            fl = pkt[TCP].flags
            flag_names = []
            if fl & 0x02: flag_names.append("SYN")
            if fl & 0x10: flag_names.append("ACK")
            if fl & 0x08: flag_names.append("PSH")
            if fl & 0x01: flag_names.append("FIN")
            if fl & 0x04: flag_names.append("RST")
            tcp_flags = " ".join(flag_names) or "—"
        elif UDP in pkt:
            dport = pkt[UDP].dport
            sport = pkt[UDP].sport
            if dport == 53 or sport == 53:
                proto = "DNS"
            elif dport in (67, 68) or sport in (67, 68):
                proto = "DHCP"
            else:
                proto = "UDP"
            info = f":{dport}"
        elif ICMP in pkt:
            proto = "ICMP"
            info = "ping"
    elif ARP in pkt:
        proto = "ARP"
        src = pkt[ARP].psrc
        dst = pkt[ARP].pdst

    meta = PROTOCOL_MAP.get(proto, PROTOCOL_MAP["OTHER"])

    direction = _direction(src, dst)
    service   = identify_service(dst) if direction == "out" else identify_service(src)

    return {
        "id":        _packet_id,
        "proto":     proto,
        "src":       src,
        "dst":       dst,
        "size":      min(size, 1500),
        "info":      info,
        "direction": direction,
        "service":   service,
        "type":      meta["type"],
        "color":     meta["color"],
        "speed":     meta["speed"] + random.uniform(-0.1, 0.2),
        "lane":      meta["lane"],
        "sport":     sport,
        "tcp_flags": tcp_flags,
        "mac_src":   mac_src,
        "mac_dst":   mac_dst,
        "ts":        time.time(),
    }


def packet_callback(pkt):
    if packet_queue is None or _loop is None:
        return
    try:
        data = classify_packet(pkt)
        asyncio.run_coroutine_threadsafe(packet_queue.put(data), _loop)
    except Exception:
        pass


# ── Demo mode ─────────────────────────────────────────────────────────────────
DEMO_PROTOS = ["TCP", "UDP", "ICMP", "DNS", "HTTP", "HTTPS", "SSH", "DHCP", "ARP"]
DEMO_LOCAL  = ["192.168.1.10", "192.168.1.1"]
DEMO_REMOTE = [
    "8.8.8.8",        # Google DNS
    "172.217.0.1",    # Google
    "142.250.0.1",    # Google
    "157.240.0.1",    # Meta
    "13.107.42.14",   # Microsoft
    "20.42.0.1",      # Microsoft Azure
    "1.1.1.1",        # Cloudflare
    "104.16.0.1",     # Cloudflare
    "198.38.120.1",   # Netflix
    "140.82.112.1",   # GitHub
    "17.172.224.1",   # Apple
    "54.230.0.1",     # AWS CloudFront
    "35.186.224.1",   # Spotify
    "66.22.196.1",    # Discord
    "23.1.0.1",       # Akamai
]

def _fake_mac():
    return ":".join(f"{random.randint(0,255):02x}" for _ in range(6))

_TCP_FLAG_COMBOS = ["SYN", "ACK", "SYN ACK", "PSH ACK", "FIN ACK", "ACK"]

async def demo_generator():
    global _packet_id
    while True:
        await asyncio.sleep(random.uniform(0.2, 0.9))
        proto = random.choice(DEMO_PROTOS)
        meta  = PROTOCOL_MAP[proto]
        direction = random.choice(["in", "out"])
        _packet_id += 1

        src, dst = (
            (random.choice(DEMO_LOCAL),  random.choice(DEMO_REMOTE))
            if direction == "out"
            else (random.choice(DEMO_REMOTE), random.choice(DEMO_LOCAL))
        )

        service = identify_service(dst) if direction == "out" else identify_service(src)
        sport   = random.randint(1024, 65535) if proto not in ("ARP",) else 0
        dport_map = {"HTTP":80,"HTTPS":443,"SSH":22,"DNS":53,"DHCP":67}
        info    = f":{dport_map.get(proto, sport)}" if sport else ""
        tcp_flags = random.choice(_TCP_FLAG_COMBOS) if proto in ("TCP","HTTP","HTTPS","SSH") else "—"

        pkt = {
            "id":        _packet_id,
            "proto":     proto,
            "src":       src,
            "dst":       dst,
            "size":      random.randint(40, 1400),
            "info":      info,
            "direction": direction,
            "service":   service,
            "type":      meta["type"],
            "color":     meta["color"],
            "speed":     meta["speed"] + random.uniform(-0.1, 0.3),
            "lane":      meta["lane"],
            "sport":     sport,
            "tcp_flags": tcp_flags,
            "mac_src":   _fake_mac(),
            "mac_dst":   _fake_mac(),
            "ts":        time.time(),
            "demo":      True,
        }
        await packet_queue.put(pkt)


async def broadcast_packets():
    while True:
        pkt = await packet_queue.get()
        dead = []
        for ws in clients:
            try:
                await ws.send_text(json.dumps(pkt))
            except Exception:
                dead.append(ws)
        for ws in dead:
            clients.remove(ws)


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.append(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        if ws in clients:
            clients.remove(ws)


app.mount("/", StaticFiles(directory=".", html=True), name="static")


if __name__ == "__main__":
    import socket as _socket, subprocess

    PORT = 8000

    def _port_busy(port):
        with _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM) as s:
            s.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1)
            try:
                s.bind(("", port))
                return False
            except OSError:
                return True

    if _port_busy(PORT):
        print(f"[backend] puerto {PORT} ocupado — liberando...")
        subprocess.run(
            f"fuser -k {PORT}/tcp 2>/dev/null; "
            f"kill $(lsof -t -i:{PORT} 2>/dev/null) 2>/dev/null",
            shell=True,
        )
        time.sleep(1.0)
        if _port_busy(PORT):
            print(f"[backend] el puerto {PORT} está ocupado por otro usuario (probablemente root).")
            print(f"[backend] libéralo con:  sudo fuser -k {PORT}/tcp")
            raise SystemExit(1)

    uvicorn.run("backend:app", host="0.0.0.0", port=PORT, reload=False)
