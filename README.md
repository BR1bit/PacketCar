# 🚗 PACKETCAR

Visualizador de tráfico de red en tiempo real con escena 3D. Los paquetes de tu red se representan como autos circulando por una autopista nocturna con skyline de servicios.

---

## Características

- **Tráfico bidireccional** — carriles separados para paquetes salientes (→) y entrantes (←)
- **10 protocolos** — TCP, UDP, ICMP, DNS, HTTP, HTTPS, SSH, DHCP, ARP y OTRO, cada uno con vehículo y color único
- **Vehículos detallados** — carrocerías facetadas, faros y luces traseras emisivas, paragolpes, alerón en el deportivo, banda de cuadros en el taxi, chimenea en el camión, moto con piloto
- **💥 Desarmar un paquete** — clic en un auto y elige *Desarmar*: el vehículo se despieza en 4 objetos que representan las capas de red (ver tabla abajo)
- **Skyline dinámico** — edificios de Google, Netflix, AWS, Cloudflare, Meta, Microsoft, Apple, GitHub, Akamai y Spotify que pulsan al recibir tráfico
- **Autos doblan al edificio** — los paquetes salientes giran hacia el edificio del servicio destino y desaparecen
- **Seguir un auto** — cámara de persecución detrás de cualquier vehículo
- **Cámara libre** — arrastra el ratón para rotar el escenario, scroll para zoom, drag vertical para altura
- **Modo pausa / órbita** — pausa el tráfico y explora la escena con órbita completa
- **Filtros de protocolo** — activa o desactiva cada protocolo desde el panel de control
- **Lluvia** — 2000 partículas de lluvia animadas
- **Modo demo** — si no se ejecuta con permisos de captura, genera tráfico simulado automáticamente
- **Feed en vivo** — panel lateral con el historial de paquetes recientes

---

## 💥 Desarmar: la analogía del auto

Al desarmar un auto, cada parte representa una capa del paquete de red:

| Parte del auto | Capa | Datos mostrados |
|---|---|---|
| 👥 **Personas** | L7 Aplicación | Servicio destino, dirección, info — más bytes = más pasajeros |
| 🚗 **Carrocería** | L4 Transporte | Protocolo, puertos, tamaño, flags TCP |
| 🔢 **Matrícula** | L3 Red | Chapa patente con la **dirección IP** escrita |
| 🔩 **Chasis** | L2 Enlace | Bastidor con placa grabada con la **MAC** (número de chasis) |

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

## 🐳 Despliegue con Docker (tráfico del servidor)

Para exponer PACKETCAR en un servidor y que los visitantes vean **el tráfico de ese servidor**:

```bash
docker compose up -d --build
```

El `docker-compose.yml` incluido usa:

- `network_mode: host` — imprescindible: Scapy captura en las interfaces reales del servidor. Con la red bridge por defecto solo vería el tráfico interno del contenedor (y caería en modo demo)
- `cap_add: NET_RAW, NET_ADMIN` — permite la captura de paquetes sin recurrir a `--privileged`
- `PORT` — con red de host el puerto se comparte con los demás servicios del servidor; cámbialo en el compose si el 8000 está ocupado

Si lo pones detrás de un reverse proxy con TLS (nginx, Caddy, Traefik), el frontend usa `wss://` automáticamente. Recuerda configurar el proxy para WebSockets (`Upgrade`/`Connection` headers) en la ruta `/ws`.

> ⚠️ **Privacidad**: los visitantes verán las IPs y puertos de todas las conexiones del servidor, incluidas las de otros usuarios conectados a tus demás servicios. Exponlo solo si eso es aceptable (o protégelo con autenticación en el proxy).

---

## Controles

| Acción | Control |
|---|---|
| Rotar escena izquierda/derecha | Arrastrar ratón horizontalmente |
| Subir/bajar cámara | Arrastrar ratón verticalmente |
| Zoom | Scroll |
| Menú de auto (Seguir / Desarmar) | Clic sobre el auto |
| Rearmar un auto desarmado | Botón 🔧 REARMAR o `Esc` |
| Soltar seguimiento | Clic en espacio vacío o `Esc` |
| Pausa / cámara libre | Botón ⏸ PAUSA o `Espacio` |
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
