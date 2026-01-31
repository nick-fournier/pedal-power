#ifndef MQTT_CLIENT_H
#define MQTT_CLIENT_H

#include <stdint.h>
#include <stdbool.h>

// Initialize MQTT client
bool mqtt_client_init(const char *broker_ip, uint16_t broker_port);

// Publish telemetry data
bool mqtt_publish_telemetry(const char *device_id, uint32_t seq, 
                             float voltage, float current, float power);

// Check if MQTT is connected
bool mqtt_is_connected(void);

#endif // MQTT_CLIENT_H
