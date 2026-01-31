#!/bin/bash
# Quick start script for Pedal Power server

set -e

echo "🚴 Pedal Power Server Quick Start"
echo "=================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker and Docker Compose first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Navigate to server directory
cd "$(dirname "$0")"

# Check if .env exists, if not create from example
if [ ! -f .env ]; then
    echo "📝 Creating .env from .env.example"
    cp .env.example .env
    echo "⚠️  Please edit .env and update the SECRET_KEY for production!"
    echo ""
fi

# Start the stack
echo "🚀 Starting the Pedal Power server stack..."
echo ""
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if services are running
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "✅ Server started successfully!"
echo ""
echo "📍 Access points:"
echo "   Dashboard:  http://localhost:8000"
echo "   MQTT Broker: localhost:1883"
echo "   PostgreSQL:  localhost:5432"
echo ""
echo "📝 Useful commands:"
echo "   View logs:      docker-compose logs -f"
echo "   Stop services:  docker-compose down"
echo "   Restart:        docker-compose restart"
echo ""
echo "🧪 Test with sample data:"
echo "   python test_mqtt_publisher.py --broker localhost --rate 10 --duration 60"
echo ""
echo "📖 For more information, see README.md and INSTALL.md"
