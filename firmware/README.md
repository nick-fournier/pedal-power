# Pedal Power Firmware

Firmware for Raspberry Pi Pico W to monitor bike pedal power and transmit telemetry via MQTT.

## Features

- ADC sampling at ~100 Hz for voltage and current measurement
- MQTT telemetry publishing at 5-10 Hz
- Local PWM control for load management
- WiFi connectivity using CYW43
- No HTTP server (MQTT only)
- LAN-only, no TLS (plain MQTT)

## Hardware Requirements

- Raspberry Pi Pico W
- Voltage sensor connected to ADC0 (GPIO26)
- Current sensor connected to ADC1 (GPIO27)
- PWM output on GPIO15 (configurable)

## Configuration

Edit the following constants in `src/main.c`:

```c
#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"
#define MQTT_BROKER_IP "192.168.1.100"
#define MQTT_BROKER_PORT 1883
#define DEVICE_ID "bike1"
```

## Building

### Prerequisites

- Pico SDK installed and `PICO_SDK_PATH` environment variable set
- CMake 3.13 or higher
- ARM GCC toolchain

### Build Steps

```bash
cd firmware
mkdir build
cd build
cmake ..
make
```

The output file `pedal_power.uf2` will be in the `build` directory.

## Flashing

1. Hold the BOOTSEL button on the Pico W
2. Connect the Pico W to your computer via USB
3. Release the BOOTSEL button
4. The Pico W will appear as a USB mass storage device
5. Copy `pedal_power.uf2` to the device
6. The Pico W will reboot and run the firmware

## MQTT Payload Format

```json
{
  "dev": "bike1",
  "seq": 123,
  "v": 12.5,
  "i": 2.3,
  "p": 28.75
}
```

- `dev`: Device identifier
- `seq`: Sequence number (increments with each publish)
- `v`: Voltage in volts
- `i`: Current in amperes
- `p`: Power in watts (calculated as v * i)

## Monitoring

Connect to the Pico W's USB serial port to see debug output:

```bash
# Linux/macOS
screen /dev/ttyACM0 115200

# Or use minicom, putty, etc.
```

## Hardware Configuration

### Voltage Sensor

- Connect to GPIO26 (ADC0)
- Voltage divider should scale input to 0-3.3V range
- Current scaling factor: `VOLTAGE_SCALE = 11.0` (adjustable in `adc_sampler.c`)

### Current Sensor

- Connect to GPIO27 (ADC1)
- Should output 0-3.3V proportional to current
- Current scaling factor: `CURRENT_SCALE = 10.0` (adjustable in `adc_sampler.c`)

### PWM Output

- GPIO15 by default (configurable via `PWM_GPIO_PIN` in `main.c`)
- 25 kHz frequency
- 0-100% duty cycle control

## License

See LICENSE file in repository root.
