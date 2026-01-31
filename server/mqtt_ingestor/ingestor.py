#!/usr/bin/env python3
"""
MQTT Ingestor for Pedal Power
Subscribes to MQTT telemetry and writes to Postgres
"""

import json
import os
import signal
import sys
import time
from datetime import datetime
from typing import Optional

import paho.mqtt.client as mqtt
import psycopg2
from psycopg2.extras import execute_values


class MQTTIngestor:
    def __init__(
        self,
        mqtt_broker: str,
        mqtt_port: int,
        mqtt_topic: str,
        db_host: str,
        db_port: int,
        db_name: str,
        db_user: str,
        db_password: str,
    ):
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_topic = mqtt_topic
        
        self.db_conn = None
        self.mqtt_client = None
        
        # Database connection parameters
        self.db_params = {
            'host': db_host,
            'port': db_port,
            'database': db_name,
            'user': db_user,
            'password': db_password,
        }
        
        self.running = True
        
    def connect_db(self):
        """Connect to PostgreSQL database"""
        try:
            self.db_conn = psycopg2.connect(**self.db_params)
            self.db_conn.autocommit = True
            print(f"Connected to database: {self.db_params['database']}")
            
            # Ensure table exists
            self.create_table()
        except Exception as e:
            print(f"Database connection error: {e}")
            raise
            
    def create_table(self):
        """Create telemetry table if it doesn't exist"""
        with self.db_conn.cursor() as cur:
            cur.execute("""
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
            """)
        print("Telemetry table ready")
        
    def on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            print(f"Connected to MQTT broker: {self.mqtt_broker}:{self.mqtt_port}")
            client.subscribe(self.mqtt_topic)
            print(f"Subscribed to topic: {self.mqtt_topic}")
        else:
            print(f"MQTT connection failed with code: {rc}")
            
    def on_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            # Parse JSON payload
            payload = json.loads(msg.payload.decode('utf-8'))
            
            # Extract fields
            device_id = payload.get('dev')
            seq = payload.get('seq')
            voltage = payload.get('v')
            current = payload.get('i')
            power = payload.get('p')
            
            # Validate required fields
            if None in (device_id, seq, voltage, current, power):
                print(f"Invalid payload: {payload}")
                return
                
            # Insert into database with server timestamp
            server_timestamp = datetime.now()
            self.insert_telemetry(server_timestamp, device_id, seq, voltage, current, power)
            
            print(f"Stored: dev={device_id} seq={seq} v={voltage:.2f} i={current:.2f} p={power:.2f}")
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
        except Exception as e:
            print(f"Error processing message: {e}")
            
    def insert_telemetry(self, server_timestamp, device_id, seq, voltage, current, power):
        """Insert telemetry data into database"""
        try:
            with self.db_conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO telemetry 
                    (server_timestamp, device_id, sequence_number, voltage, current, power)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (server_timestamp, device_id, seq, voltage, current, power)
                )
        except Exception as e:
            print(f"Database insert error: {e}")
            # Attempt to reconnect
            self.connect_db()
            
    def start(self):
        """Start the MQTT ingestor"""
        # Connect to database
        self.connect_db()
        
        # Set up MQTT client
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        
        # Connect to MQTT broker
        print(f"Connecting to MQTT broker: {self.mqtt_broker}:{self.mqtt_port}")
        self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
        
        # Start MQTT loop
        self.mqtt_client.loop_start()
        
        # Keep running
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            
        self.stop()
        
    def stop(self):
        """Stop the MQTT ingestor"""
        self.running = False
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        if self.db_conn:
            self.db_conn.close()
        print("Stopped")


def main():
    # Configuration from environment variables
    mqtt_broker = os.getenv('MQTT_BROKER', 'mosquitto')
    mqtt_port = int(os.getenv('MQTT_PORT', '1883'))
    mqtt_topic = os.getenv('MQTT_TOPIC', 'bike/telemetry')
    
    db_host = os.getenv('DB_HOST', 'postgres')
    db_port = int(os.getenv('DB_PORT', '5432'))
    db_name = os.getenv('DB_NAME', 'pedalpower')
    db_user = os.getenv('DB_USER', 'pedalpower')
    db_password = os.getenv('DB_PASSWORD', 'pedalpower')
    
    print("=== MQTT Ingestor Starting ===")
    print(f"MQTT: {mqtt_broker}:{mqtt_port} topic={mqtt_topic}")
    print(f"DB: {db_host}:{db_port}/{db_name}")
    
    ingestor = MQTTIngestor(
        mqtt_broker=mqtt_broker,
        mqtt_port=mqtt_port,
        mqtt_topic=mqtt_topic,
        db_host=db_host,
        db_port=db_port,
        db_name=db_name,
        db_user=db_user,
        db_password=db_password,
    )
    
    # Handle signals
    def signal_handler(sig, frame):
        print("\nReceived signal, shutting down...")
        ingestor.stop()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    ingestor.start()


if __name__ == '__main__':
    main()
