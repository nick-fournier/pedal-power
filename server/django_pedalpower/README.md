# Django Pedal Power App

A reusable Django app for bike power monitoring with MQTT telemetry ingestion, REST API, and dashboard.

## Features

- **REST API** for telemetry data access
- **1 Hz Downsampling** - Averages raw samples to 1 Hz
- **Session Detection** - Automatically detects workout sessions based on power thresholds
- **Energy Calculation** - Computes cumulative Wh (watt-hours) from power data
- **Web Dashboard** - Real-time visualization with charts
- **Django Admin** - Browse telemetry data

## Installation

### Using UV (Recommended)

```bash
# Install from source
uv pip install git+https://github.com/nick-fournier/pedal-power.git#subdirectory=server/django_pedalpower

# Or install from local path
cd server/django_pedalpower
uv pip install -e .

# With optional dependencies
uv pip install -e ".[dev,server]"
```

### Using pip

```bash
pip install git+https://github.com/nick-fournier/pedal-power.git#subdirectory=server/django_pedalpower
```

## Integration into Your Django Project

### 1. Add to INSTALLED_APPS

In your Django project's `settings.py`:

```python
INSTALLED_APPS = [
    # ... your other apps
    'rest_framework',
    'corsheaders',  # If you need CORS support
    'pedalpower',
]
```

### 2. Configure Middleware (Optional)

If you need CORS support for API access:

```python
MIDDLEWARE = [
    # ...
    'corsheaders.middleware.CorsMiddleware',
    # ...
]

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True  # Or configure specific origins
```

### 3. Add URL Patterns

In your project's `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ... your other URLs
    path('pedalpower/', include('pedalpower.urls')),
]
```

This will make the app available at:
- Dashboard: `/pedalpower/`
- API: `/pedalpower/api/telemetry/`

### 4. Configure Database

The app uses an external table managed by the MQTT ingestor. Ensure your database settings point to the same PostgreSQL database:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pedalpower',
        'USER': 'pedalpower',
        'PASSWORD': 'pedalpower',
        'HOST': 'postgres',
        'PORT': '5432',
    }
}
```

### 5. Run Migrations (Optional)

Since the table is managed externally, migrations aren't strictly necessary, but you can run them if needed:

```bash
python manage.py migrate
```

## API Endpoints

### List Telemetry Data

```
GET /pedalpower/api/telemetry/
```

Query parameters:
- `device_id` - Filter by device (e.g., "bike1")
- `start_time` - ISO 8601 timestamp (e.g., "2024-01-01T00:00:00Z")
- `end_time` - ISO 8601 timestamp

### Get Downsampled Data (1 Hz)

```
GET /pedalpower/api/telemetry/downsampled/
```

Returns data averaged to 1-second intervals with cumulative energy (Wh).

Query parameters: Same as above

Response:
```json
[
  {
    "timestamp": "2024-01-01T12:00:00Z",
    "avg_voltage": 12.5,
    "avg_current": 2.0,
    "avg_power": 25.0,
    "energy_wh": 0.0069
  },
  ...
]
```

### Get Detected Sessions

```
GET /pedalpower/api/telemetry/sessions/
```

Query parameters:
- `device_id` - Filter by device
- `start_time` - ISO 8601 timestamp
- `end_time` - ISO 8601 timestamp
- `threshold` - Power threshold in watts (default: 10)
- `gap_seconds` - Max gap between samples before ending session (default: 30)

Response:
```json
[
  {
    "session_id": 1,
    "device_id": "bike1",
    "start_time": "2024-01-01T12:00:00Z",
    "end_time": "2024-01-01T12:30:00Z",
    "duration_seconds": 1800,
    "total_energy_wh": 450.0,
    "avg_power": 90.0,
    "max_power": 150.0
  },
  ...
]
```

## Dashboard

Access the dashboard at `/pedalpower/` to view:
- Real-time power charts
- Cumulative energy overlay
- Session list
- Auto-refresh controls

## Customization

### Custom Template

Override the dashboard template by creating:
```
your_project/templates/pedalpower/dashboard.html
```

### Custom API URL

If you mount the app at a different URL, update the `API_BASE` constant in the dashboard template:

```javascript
const API_BASE = '/your-custom-path/api';
```

### Custom Styling

Add custom CSS by extending the template or including your own stylesheets.

## Development

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black pedalpower/
uv run ruff check pedalpower/
```

## Dependencies

Core dependencies (automatically installed):
- Django >= 4.2, < 5.0
- djangorestframework >= 3.14, < 4.0
- psycopg2-binary >= 2.9, < 3.0
- django-cors-headers >= 4.0, < 5.0
- paho-mqtt >= 1.6.1, < 2.0.0

Optional dependencies:
- `dev`: pytest, black, ruff (for development)
- `server`: gunicorn (for production deployment)

## Database Schema

The app expects a `telemetry` table (created by the MQTT ingestor):

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

## Integration with MQTT Ingestor

This app reads data written by the MQTT ingestor service. Ensure both are configured to use the same database.

See the main repository for MQTT ingestor setup: [../mqtt_ingestor/](../mqtt_ingestor/)

## License

MIT License - see LICENSE file in repository root.

## Support

For issues specific to this Django app, please open an issue on GitHub.
