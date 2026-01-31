-- Initialize database for Pedal Power

-- Create database (run as postgres superuser)
-- CREATE DATABASE pedalpower;
-- CREATE USER pedalpower WITH PASSWORD 'pedalpower';
-- GRANT ALL PRIVILEGES ON DATABASE pedalpower TO pedalpower;

-- Connect to pedalpower database and create table
-- This will be created by the MQTT ingestor, but here for reference

CREATE TABLE IF NOT EXISTS telemetry (
    id SERIAL PRIMARY KEY,
    server_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    device_id VARCHAR(50) NOT NULL,
    sequence_number INTEGER NOT NULL,
    voltage FLOAT NOT NULL,
    current FLOAT NOT NULL,
    power FLOAT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_telemetry_device_timestamp 
ON telemetry(device_id, server_timestamp);

CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp
ON telemetry(server_timestamp);
