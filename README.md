# 🚗 PACKETCAR

Visualizador de tráfico de red en tiempo real con escena 3D. Los paquetes de tu red se representan como autos circulando por una autopista nocturna con skyline de servicios.

---

## Características

- **Tráfico bidireccional** — carriles separados para paquetes salientes (→) y entrantes (←)
- **11 protocolos** — TCP, UDP, ICMP, DNS, HTTP, HTTPS, SSH, DHCP, ARP y OTRO, cada uno con vehículo y color único
- **Skyline dinámico** — edificios de Google, Netflix, AWS, Cloudflare, Meta, Microsoft, Apple, GitHub, Akamai y Spotify que pulsan al recibir tráfico
- **Autos doblan al edificio** — los paquetes salientes giran hacia el edificio del servicio destino y desaparecen
- **Seguir un auto** — clic sobre cualquier auto para activar la cámara de seguimiento
- **Cámara libre** — arrastra el ratón para rotar el escenario, scroll para zoom, drag vertical para altura
- **Modo pausa / órbita** — pausa el tráfico y explora la escena con órbita completa
- **Filtros de protocolo** — activa o desactiva cada protocolo desde el panel de control
- **Lluvia** — 2000 partículas de lluvia animadas
- **Modo demo** — si no se ejecuta con permisos de captura, genera tráfico simulado automáticamente
- **Feed en vivo** — panel lateral con el historial de paquetes recientes

---

## Requisitos

- Python 3.10+
- pip
- (Opcional) Permisos de root/sudo para captura real de paquetes con Scapy

---

## Instalación

```bash
# 1. Clona el repositorio
git clone https://github.com/BR1bit/PacketCar.git
cd PacketCar

# 2. Crea un entorno virtual (recomendado)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instala las dependencias
pip install -r requirements.txt
```

---

## Uso

### Modo demo (sin permisos especiales)
```bash
python backend.py
```

### Captura real de paquetes
```bash
sudo python backend.py
```

Abre el navegador en [http://localhost:8000](http://localhost:8000)

---

## Controles

| Acción | Control |
|---|---|
| Rotar escena izquierda/derecha | Arrastrar ratón horizontalmente |
| Subir/bajar cámara | Arrastrar ratón verticalmente |
| Zoom | Scroll |
| Seguir un auto | Clic sobre el auto |
| Soltar seguimiento | Clic en espacio vacío o `Esc` |
| Pausa / cámara libre | Botón ⏸ PAUSA |
| Filtrar protocolos | Botones de protocolo en el panel |

---

## Stack

| Componente | Tecnología |
|---|---|
| Frontend 3D | [Three.js](https://threejs.org/) r165 |
| Backend | [FastAPI](https://fastapi.tiangolo.com/) + WebSockets |
| Captura de paquetes | [Scapy](https://scapy.net/) |
| Servidor ASGI | [Uvicorn](https://www.uvicorn.org/) |

---

## Protocolos y vehículos

| Protocolo | Vehículo | Color |
|---|---|---|
| TCP | Sedán | Azul |
| UDP | Deportivo | Ámbar |
| ICMP | Moto | Rojo |
| DNS | Taxi | Amarillo |
| HTTP | Camión | Verde |
| HTTPS | Camión | Violeta |
| SSH | Deportivo | Teal |
| DHCP | Furgoneta | Rosa |
| ARP | Furgoneta | Púrpura |
