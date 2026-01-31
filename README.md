# ⚡ Pedal Power

A complete monorepo for bike power monitoring using Raspberry Pi Pico W and a Python/Django server stack.

## Overview

Pedal Power is an IoT system for monitoring and analyzing bicycle pedal power output. It consists of:

1. **Firmware** (Pico W in C) - Samples ADC at ~100 Hz, publishes telemetry via MQTT at 5-10 Hz
2. **Server** (Mosquitto + Python + Postgres + Django) - Ingests data, provides API, and serves web dashboard

## Architecture

```
┌─────────────┐
│  Pico W     │  ADC Sampling @ 100 Hz
│  Firmware   │  MQTT Publish @ 5-10 Hz
└──────┬──────┘
       │ WiFi (LAN only, no TLS)
       │ MQTT: {"dev":"bike1","seq":N,"v":V,"i":I,"p":P}
       ▼
┌─────────────┐
│ Mosquitto   │  MQTT Broker
│   Broker    │  Port 1883
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    MQTT     │  Python Subscriber
│  Ingestor   │  → Postgres (raw samples + server timestamp)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ PostgreSQL  │  Telemetry Storage
│  Database   │  (Raw samples)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Django    │  REST API
│     API     │  - Downsample to 1 Hz
│             │  - Session detection
│             │  - Energy calculations
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Web UI    │  Dashboard
│             │  - Real-time charts
│             │  - Cumulative Wh overlay
│             │  - Session list
└─────────────┘
```

## Features

### Firmware
- ✅ Raspberry Pi Pico W (RP2040 + CYW43)
- ✅ ADC sampling at ~100 Hz (voltage, current)
- ✅ MQTT telemetry publishing at 5-10 Hz
- ✅ Local PWM control
- ✅ WiFi connectivity (LAN only)
- ✅ No HTTP server (MQTT only)
- ✅ No TLS (plain MQTT)

### Server
- ✅ Mosquitto MQTT broker
- ✅ Python MQTT ingestor with server timestamps
- ✅ PostgreSQL for raw sample storage
- ✅ Django REST API
  - Downsampling to 1 Hz
  - Session detection by power thresholds
  - Cumulative energy (Wh) calculation
- ✅ Web UI with polling and plotting
- ✅ Docker Compose deployment

## Quick Start

**See [INSTALL.md](INSTALL.md) for complete installation guide.**

### Firmware Setup

See [firmware/README.md](firmware/README.md) for detailed instructions.

```bash
cd firmware
# Configure WiFi and MQTT broker in src/main.c
mkdir build && cd build
cmake ..
make
# Flash pedal_power.uf2 to Pico W
```

### Server Setup

See [server/README.md](server/README.md) for detailed instructions.

```bash
cd server
docker-compose up -d
```

Access the dashboard at: http://localhost:8000

## Repository Structure

```
pedal-power/
├── firmware/               # Pico W firmware (C)
│   ├── src/
│   │   ├── main.c         # Main application
│   │   ├── mqtt_client.*  # MQTT client using lwIP
│   │   ├── adc_sampler.*  # ADC sampling at 100 Hz
│   │   └── pwm_control.*  # PWM output control
│   ├── CMakeLists.txt     # Build configuration
│   └── README.md
│
├── server/                # Server components
│   ├── mosquitto/         # MQTT broker config
│   ├── mqtt_ingestor/     # Python MQTT → Postgres
│   ├── django_api/        # Django API + Web UI
│   ├── postgres/          # Database init scripts
│   ├── docker-compose.yml # Complete stack
│   └── README.md
│
├── .gitignore
├── LICENSE
└── README.md
```

## Hardware Requirements

### Firmware
- Raspberry Pi Pico W
- Voltage sensor (→ ADC0/GPIO26)
  - Should scale to 0-3.3V range
- Current sensor (→ ADC1/GPIO27)
  - Should output 0-3.3V proportional to current
- Optional: Load connected to PWM output (GPIO15)

### Server
- Any computer capable of running Docker
- Network connectivity to Pico W

## Data Flow

1. **Pico W** samples ADC at 100 Hz (voltage, current)
2. Moving average filter smooths readings
3. MQTT publish at 5-10 Hz: `{"dev":"bike1","seq":N,"v":V,"i":I,"p":P}`
4. **MQTT Ingestor** receives messages and writes to Postgres with server timestamp
5. **Django API** queries Postgres:
   - Downsamples to 1 Hz (averages per second)
   - Detects sessions (power > threshold)
   - Calculates cumulative energy (Wh)
6. **Web UI** polls API every 5 seconds and updates charts

## API Examples

### Get downsampled data (1 Hz)
```bash
curl "http://localhost:8000/api/telemetry/downsampled/?device_id=bike1"
```

### Get detected sessions
```bash
curl "http://localhost:8000/api/telemetry/sessions/?device_id=bike1&threshold=10"
```

## Configuration

### Firmware
Edit `firmware/src/main.c`:
- `WIFI_SSID` and `WIFI_PASSWORD`
- `MQTT_BROKER_IP` (e.g., "192.168.1.100")
- `DEVICE_ID` (default: "bike1")

### Server
Edit `server/docker-compose.yml` for:
- Database credentials
- MQTT topic name
- Django secret key (production)

## Development

### Testing MQTT

Send test message:
```bash
mosquitto_pub -h localhost -t bike/telemetry \
  -m '{"dev":"bike1","seq":1,"v":12.5,"i":2.0,"p":25.0}'
```

Subscribe to topic:
```bash
mosquitto_sub -h localhost -t bike/telemetry
```

### Database Query

```bash
docker-compose exec postgres psql -U pedalpower -d pedalpower
SELECT * FROM telemetry ORDER BY server_timestamp DESC LIMIT 10;
```

## Production Considerations

- [ ] Change Django `SECRET_KEY`
- [ ] Use strong database passwords
- [ ] Enable HTTPS (nginx reverse proxy)
- [ ] Add API authentication
- [ ] Set up database backups
- [ ] Configure resource limits
- [ ] Add monitoring/alerting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Raspberry Pi Foundation for Pico SDK
- Eclipse Foundation for Mosquitto
- lwIP team for the MQTT client library

## Support

For issues and questions:
- Check the README files in `/firmware` and `/server` directories
- Open an issue on GitHub
- Review troubleshooting sections in documentation