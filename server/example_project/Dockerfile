FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN pip install uv

# Copy Django app source
COPY django_pedalpower /tmp/django_pedalpower

# Copy example project
COPY example_project /app

# Install dependencies using UV
RUN cd /tmp/django_pedalpower && uv pip install --system -e .
RUN cd /app && uv pip install --system -r <(echo "gunicorn>=21.0,<22.0")

# Collect static files
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "example_project.wsgi:application"]
