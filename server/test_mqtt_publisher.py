#!/usr/bin/env python3
"""
Test script to send sample MQTT telemetry data
Useful for testing the server stack without hardware
"""

import json
import time
import random
import argparse
import paho.mqtt.client as mqtt


def generate_telemetry(device_id, seq):
    """Generate realistic telemetry data"""
    # Simulate realistic power output (pedaling)
    # Power varies between 0-150W with some randomness
    base_power = 80 + 40 * random.random()
    voltage = 12.0 + random.random() * 2.0  # 12-14V
    current = base_power / voltage  # Calculate current from power
    
    return {
        "dev": device_id,
        "seq": seq,
        "v": round(voltage, 2),
        "i": round(current, 2),
        "p": round(voltage * current, 2)
    }


def on_connect(client, userdata, flags, rc):
    """MQTT connection callback"""
    if rc == 0:
        print(f"Connected to MQTT broker")
    else:
        print(f"Connection failed with code {rc}")


def main():
    parser = argparse.ArgumentParser(description='Send test MQTT telemetry data')
    parser.add_argument('--broker', default='localhost', help='MQTT broker address')
    parser.add_argument('--port', type=int, default=1883, help='MQTT broker port')
    parser.add_argument('--topic', default='bike/telemetry', help='MQTT topic')
    parser.add_argument('--device', default='bike1', help='Device ID')
    parser.add_argument('--rate', type=int, default=10, help='Publish rate (Hz)')
    parser.add_argument('--duration', type=int, default=60, help='Duration (seconds), 0 for infinite')
    parser.add_argument('--power-on', action='store_true', help='Simulate power being on (else random)')
    
    args = parser.parse_args()
    
    # Create MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    
    try:
        print(f"Connecting to MQTT broker at {args.broker}:{args.port}")
        client.connect(args.broker, args.port, 60)
        client.loop_start()
        
        # Wait for connection
        time.sleep(1)
        
        print(f"Publishing telemetry to topic '{args.topic}' at {args.rate} Hz")
        print(f"Device ID: {args.device}")
        print("Press Ctrl+C to stop\n")
        
        seq = 0
        start_time = time.time()
        interval = 1.0 / args.rate
        
        while True:
            # Check duration
            if args.duration > 0 and (time.time() - start_time) >= args.duration:
                print("\nDuration reached, stopping")
                break
            
            # Generate and publish telemetry
            if args.power_on:
                telemetry = generate_telemetry(args.device, seq)
            else:
                # Random on/off periods
                if random.random() > 0.3:  # 70% chance of power
                    telemetry = generate_telemetry(args.device, seq)
                else:
                    # Low power (coasting)
                    telemetry = {
                        "dev": args.device,
                        "seq": seq,
                        "v": 12.0,
                        "i": 0.1,
                        "p": 1.2
                    }
            
            payload = json.dumps(telemetry)
            client.publish(args.topic, payload)
            
            print(f"[{seq:04d}] {payload}")
            
            seq += 1
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        print("Disconnected")


if __name__ == '__main__':
    main()
