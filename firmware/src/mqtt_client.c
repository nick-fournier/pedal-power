#include "mqtt_client.h"
#include "pico/stdlib.h"
#include "lwip/apps/mqtt.h"
#include "lwip/ip_addr.h"
#include <stdio.h>
#include <string.h>

#define MQTT_TOPIC "bike/telemetry"
#define MQTT_QOS 0

static mqtt_client_t *mqtt_client = NULL;
static bool mqtt_connected = false;

// MQTT connection callback
static void mqtt_connection_cb(mqtt_client_t *client, void *arg, mqtt_connection_status_t status) {
    if (status == MQTT_CONNECT_ACCEPTED) {
        printf("MQTT connected\n");
        mqtt_connected = true;
    } else {
        printf("MQTT connection failed: %d\n", status);
        mqtt_connected = false;
    }
}

// MQTT request callback
static void mqtt_request_cb(void *arg, err_t err) {
    if (err != ERR_OK) {
        printf("MQTT request failed: %d\n", err);
    }
}

bool mqtt_client_init(const char *broker_ip, uint16_t broker_port) {
    mqtt_client = mqtt_client_new();
    if (mqtt_client == NULL) {
        printf("Failed to create MQTT client\n");
        return false;
    }

    struct mqtt_connect_client_info_t ci;
    memset(&ci, 0, sizeof(ci));
    ci.client_id = "pico_bike1";
    ci.keep_alive = 60;

    ip_addr_t broker_addr;
    if (!ipaddr_aton(broker_ip, &broker_addr)) {
        printf("Invalid broker IP\n");
        return false;
    }

    err_t err = mqtt_client_connect(mqtt_client, &broker_addr, broker_port, 
                                     mqtt_connection_cb, NULL, &ci);
    if (err != ERR_OK) {
        printf("MQTT connect failed: %d\n", err);
        return false;
    }

    return true;
}

bool mqtt_publish_telemetry(const char *device_id, uint32_t seq, 
                             float voltage, float current, float power) {
    if (!mqtt_connected || mqtt_client == NULL) {
        return false;
    }

    char payload[128];
    snprintf(payload, sizeof(payload), 
             "{\"dev\":\"%s\",\"seq\":%lu,\"v\":%.2f,\"i\":%.2f,\"p\":%.2f}",
             device_id, (unsigned long)seq, voltage, current, power);

    err_t err = mqtt_publish(mqtt_client, MQTT_TOPIC, payload, strlen(payload),
                             MQTT_QOS, 0, mqtt_request_cb, NULL);
    
    return (err == ERR_OK);
}

bool mqtt_is_connected(void) {
    return mqtt_connected;
}
