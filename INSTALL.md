# Pedal Power Installation Guide

Complete step-by-step guide to set up the Pedal Power system.

## Prerequisites

### For Firmware
- Raspberry Pi Pico W
- Pico SDK (or set `PICO_SDK_FETCH_FROM_GIT=1` to auto-download)
- CMake 3.13+
- ARM GCC toolchain (`arm-none-eabi-gcc`)
- Voltage and current sensors
- USB cable for programming

### For Server
- Docker and Docker Compose
- Or: Python 3.11+, PostgreSQL 15+, Mosquitto MQTT broker
- UV package manager (optional but recommended)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/nick-fournier/pedal-power.git
cd pedal-power
```

### 2. Set Up the Server

#### Option A: Using Docker (Recommended)

```bash
cd server
docker-compose up -d
```

Wait for all services to start (about 30 seconds). Verify:
```bash
docker-compose ps
```

All services should show "Up" status.

Access the dashboard at: http://localhost:8000

#### Option B: Manual Installation with UV

**Install UV:**
```bash
pip install uv
```

**Start PostgreSQL:**
```bash
# Using your system's PostgreSQL or Docker
docker run -d --name pedalpower-postgres \
  -e POSTGRES_DB=pedalpower \
  -e POSTGRES_USER=pedalpower \
  -e POSTGRES_PASSWORD=pedalpower \
  -p 5432:5432 \
  postgres:15-alpine

# Initialize database
psql -h localhost -U pedalpower -d pedalpower -f server/postgres/init.sql
```

**Start Mosquitto:**
```bash
# Using your system's Mosquitto or Docker
docker run -d --name pedalpower-mosquitto \
  -p 1883:1883 \
  -v $(pwd)/server/mosquitto/mosquitto.conf:/mosquitto/config/mosquitto.conf \
  eclipse-mosquitto:2
```

**Start MQTT Ingestor:**
```bash
cd server/mqtt_ingestor
uv pip install -r requirements.txt
export MQTT_BROKER=localhost
export DB_HOST=localhost
python ingestor.py
```

**Start Django Server:**
```bash
cd server/example_project
uv pip install -e ../django_pedalpower
export DB_HOST=localhost
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### 3. Set Up the Firmware

**Configure WiFi and MQTT:**

Edit `firmware/src/main.c` and update:
```c
#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"
#define MQTT_BROKER_IP "192.168.1.100"  // IP of your server
#define DEVICE_ID "bike1"
```

**Build the Firmware:**

```bash
cd firmware
mkdir build
cd build

# Set Pico SDK path if not in environment
export PICO_SDK_PATH=/path/to/pico-sdk

# Or let CMake fetch it automatically
export PICO_SDK_FETCH_FROM_GIT=1

cmake ..
make
```

This creates `pedal_power.uf2` in the build directory.

**Flash to Pico W:**

1. Hold the BOOTSEL button on your Pico W
2. Connect it to your computer via USB
3. Release the BOOTSEL button
4. The Pico W appears as a USB drive
5. Copy `build/pedal_power.uf2` to the drive
6. The Pico W will reboot and start running the firmware

### 4. Verify the System

**Check Firmware:**

Connect to the Pico W's USB serial:
```bash
# Linux/macOS
screen /dev/ttyACM0 115200

# You should see output like:
# === Pedal Power Firmware Starting ===
# Connecting to WiFi...
# WiFi connected
# Connecting to MQTT broker...
# MQTT connected
# === Firmware Initialized ===
```

**Check MQTT Messages:**

Subscribe to the MQTT topic:
```bash
mosquitto_sub -h localhost -t bike/telemetry
```

You should see JSON messages like:
```json
{"dev":"bike1","seq":1,"v":12.5,"i":2.0,"p":25.0}
{"dev":"bike1","seq":2,"v":12.6,"i":2.1,"p":26.5}
```

**Check Database:**

```bash
docker-compose exec postgres psql -U pedalpower -d pedalpower \
  -c "SELECT * FROM telemetry ORDER BY id DESC LIMIT 5;"
```

**Check Dashboard:**

Open http://localhost:8000 in your browser. You should see:
- Real-time power charts updating
- Current power, energy, and stats
- Session detection (if power is above threshold)

### 5. Hardware Connections

Connect your sensors to the Pico W:

**Voltage Sensor:**
- Connect to GPIO26 (ADC0)
- Should output 0-3.3V (use voltage divider if needed)
- Adjust `VOLTAGE_SCALE` in `firmware/src/adc_sampler.c` for your sensor

**Current Sensor:**
- Connect to GPIO27 (ADC1)
- Should output 0-3.3V proportional to current
- Adjust `CURRENT_SCALE` in `firmware/src/adc_sampler.c` for your sensor

**PWM Output (optional):**
- GPIO15 by default
- Can control load or indicator

**Ground:**
- Connect all grounds together (Pico, sensors, power supply)

## Troubleshooting

### Firmware won't connect to WiFi

- Check SSID and password in `main.c`
- Ensure WiFi is 2.4 GHz (Pico W doesn't support 5 GHz)
- Check WiFi signal strength

### Firmware won't connect to MQTT

- Verify broker IP is correct
- Check that server is running: `docker-compose ps`
- Test MQTT manually: `mosquitto_pub -h <broker_ip> -t test -m "hello"`

### No data in database

- Check MQTT ingestor logs: `docker-compose logs mqtt_ingestor`
- Verify topic matches between firmware and ingestor
- Check database connection in ingestor

### Dashboard shows no data

- Check time range selector (may need to adjust)
- Verify API endpoint: `curl http://localhost:8000/pedalpower/api/telemetry/`
- Check browser console for errors

### Build errors (firmware)

- Ensure Pico SDK is installed or `PICO_SDK_FETCH_FROM_GIT=1` is set
- Check that ARM toolchain is installed: `arm-none-eabi-gcc --version`
- Try: `rm -rf build && mkdir build && cd build && cmake .. && make`

## Next Steps

1. **Calibrate Sensors**: Measure known values and adjust scale factors
2. **Secure the System**: Change default passwords, add authentication
3. **Add More Devices**: Flash multiple Picos with different device IDs
4. **Customize Dashboard**: Modify templates or add features
5. **Set Up Backups**: Configure PostgreSQL backups
6. **Production Deploy**: Use nginx reverse proxy, HTTPS, etc.

## Support

- Check README files in `/firmware` and `/server` directories
- Review code comments for implementation details
- Open an issue on GitHub for bugs or questions

## License

MIT License - see LICENSE file for details.
