# Pedal Power Server

Server infrastructure for the Pedal Power bike monitoring system.

## Architecture

The server consists of four main components:

1. **Mosquitto MQTT Broker** - Receives telemetry from Pico W devices
2. **MQTT Ingestor** - Python service that subscribes to MQTT and writes to Postgres
3. **PostgreSQL Database** - Stores raw telemetry samples with server timestamps
4. **Django App** - Reusable Django app providing REST API and web dashboard

## Features

- **Raw Data Storage**: All telemetry samples stored with server-side timestamps
- **1 Hz Downsampling**: API endpoint that averages samples to 1 Hz
- **Session Detection**: Automatically detects workout sessions based on power thresholds
- **Energy Calculation**: Computes cumulative Wh (watt-hours) from power data
- **Real-time Dashboard**: Web UI that polls and displays power/energy charts
- **UV Package Management**: Uses UV for fast, reliable Python dependency management

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Pico W device with firmware (see `/firmware` directory)

### Starting the Server

```bash
cd server
docker-compose up -d
```

This will start all services:
- Mosquitto MQTT on port 1883
- PostgreSQL on port 5432
- Django API on port 8000

### Accessing the Dashboard

Open your browser to: http://localhost:8000

The dashboard is served by the example Django project that includes the `pedalpower` app.

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f mqtt_ingestor
docker-compose logs -f django_api
```

### Stopping the Server

```bash
docker-compose down
```

## Directory Structure

```
server/
├── mosquitto/              # MQTT broker configuration
│   └── mosquitto.conf
├── mqtt_ingestor/          # Python MQTT → Postgres service
│   ├── ingestor.py
│   ├── requirements.txt
│   └── Dockerfile
├── postgres/               # Database initialization
│   └── init.sql
├── django_pedalpower/      # Reusable Django app (installable package)
│   ├── pedalpower/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── serializers.py
│   │   ├── admin.py
│   │   └── templates/
│   ├── pyproject.toml      # UV/pip package config
│   └── README.md
├── example_project/        # Example Django project using the app
│   ├── example_project/
│   │   ├── settings.py
│   │   └── urls.py
│   ├── manage.py
│   ├── pyproject.toml
│   └── Dockerfile
├── docker-compose.yml      # Complete stack orchestration
└── README.md
```

## Using the Django App in Your Project

The `django_pedalpower` directory contains a reusable Django app that can be installed into any Django project.

### Installation with UV

```bash
# From the repository
uv pip install -e server/django_pedalpower

# Or from git
uv pip install git+https://github.com/nick-fournier/pedal-power.git#subdirectory=server/django_pedalpower
```

### Integration

See [django_pedalpower/README.md](django_pedalpower/README.md) for detailed integration instructions.

Quick setup in your Django project:

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'corsheaders',
    'pedalpower',
]

# urls.py
urlpatterns = [
    # ...
    path('pedalpower/', include('pedalpower.urls')),
]
```

## API Endpoints

### Get Raw Telemetry

```
GET /pedalpower/api/telemetry/?device_id=bike1&start_time=2024-01-01T00:00:00Z
```

Parameters:
- `device_id` (optional): Filter by device
- `start_time` (optional): ISO 8601 timestamp
- `end_time` (optional): ISO 8601 timestamp

### Get Downsampled Data (1 Hz)

```
GET /pedalpower/api/telemetry/downsampled/?device_id=bike1
```

Returns averaged samples at 1 Hz with cumulative energy (Wh).

### Get Detected Sessions

```
GET /pedalpower/api/telemetry/sessions/?device_id=bike1&threshold=10&gap_seconds=30
```

Parameters:
- `threshold` (default: 10): Power threshold in watts to consider active
- `gap_seconds` (default: 30): Maximum gap between samples before ending session

Returns sessions with:
- Start/end times
- Duration
- Total energy (Wh)
- Average and peak power

## Configuration

### Environment Variables

Edit `docker-compose.yml` to customize:

**MQTT Ingestor:**
- `MQTT_BROKER`: Mosquitto hostname (default: mosquitto)
- `MQTT_PORT`: MQTT port (default: 1883)
- `MQTT_TOPIC`: Topic to subscribe to (default: bike/telemetry)
- `DB_*`: Database connection settings

**Django API:**
- `DEBUG`: Enable debug mode (default: False)
- `SECRET_KEY`: Django secret key (change in production!)
- `ALLOWED_HOSTS`: Comma-separated hostnames
- `DB_*`: Database connection settings

### Mosquitto Configuration

Edit `mosquitto/mosquitto.conf` to customize MQTT broker settings.

## Database Schema

### telemetry table

```sql
CREATE TABLE telemetry (
    id SERIAL PRIMARY KEY,
    server_timestamp TIMESTAMP NOT NULL,
    device_id VARCHAR(50) NOT NULL,
    sequence_number INTEGER NOT NULL,
    voltage FLOAT NOT NULL,
    current FLOAT NOT NULL,
    power FLOAT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

Indexes:
- `(device_id, server_timestamp)` - For device-specific queries
- `(server_timestamp)` - For time-range queries

## Development

### Running Without Docker

**PostgreSQL:**
```bash
# Install and start PostgreSQL
psql -U postgres -f postgres/init.sql
```

**Mosquitto:**
```bash
mosquitto -c mosquitto/mosquitto.conf
```

**MQTT Ingestor:**
```bash
cd mqtt_ingestor
pip install -r requirements.txt
export MQTT_BROKER=localhost
export DB_HOST=localhost
python ingestor.py
```

**Django App (using UV):**
```bash
cd example_project
uv pip install -e ../django_pedalpower
export DB_HOST=localhost
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### Testing the Stack

**Send test MQTT messages manually:**

```bash
mosquitto_pub -h localhost -t bike/telemetry \
  -m '{"dev":"bike1","seq":1,"v":12.5,"i":2.0,"p":25.0}'
```

**Or use the test publisher script:**

```bash
cd server
python test_mqtt_publisher.py --broker localhost --rate 10 --duration 60

# Options:
# --broker: MQTT broker address (default: localhost)
# --rate: Publish rate in Hz (default: 10)
# --duration: Duration in seconds (default: 60, 0 for infinite)
# --power-on: Simulate continuous power (else random on/off periods)
# --device: Device ID (default: bike1)
```

**Check database:**

```bash
docker-compose exec postgres psql -U pedalpower -d pedalpower \
  -c "SELECT * FROM telemetry ORDER BY id DESC LIMIT 10;"
```

## Monitoring

### Health Checks

- Mosquitto: `mosquitto_sub -h localhost -t \$SYS/#`
- PostgreSQL: `docker-compose exec postgres pg_isready`
- Django: `curl http://localhost:8000/pedalpower/api/telemetry/`

### Performance

The system is designed to handle:
- Multiple devices publishing at 5-10 Hz
- Dashboard polling at 5-second intervals
- Efficient downsampling via database aggregation queries

## Production Deployment

For production:

1. **Change Secret Key**: Set a secure `SECRET_KEY` in Django
2. **Use Strong Passwords**: Change default database passwords
3. **Enable TLS**: Configure HTTPS for Django (use nginx reverse proxy)
4. **Add Authentication**: Protect the API with Django authentication
5. **Backup Database**: Set up regular PostgreSQL backups
6. **Monitor Logs**: Use logging aggregation (e.g., ELK stack)
7. **Resource Limits**: Set appropriate CPU/memory limits in docker-compose

## Troubleshooting

### MQTT Ingestor not receiving messages

Check:
1. Mosquitto is running: `docker-compose ps mosquitto`
2. Pico W is connected to correct broker IP
3. MQTT topic matches in firmware and ingestor config

### No data in database

Check:
1. MQTT ingestor logs: `docker-compose logs mqtt_ingestor`
2. Database connection: `docker-compose exec postgres psql -U pedalpower`
3. Table exists: `\dt` in psql

### Dashboard shows no data

Check:
1. API is accessible: `curl http://localhost:8000/pedalpower/api/telemetry/`
2. Browser console for JavaScript errors
3. Time range selector includes data timestamps

## License

See LICENSE file in repository root.
