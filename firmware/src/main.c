#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"
#include "hardware/adc.h"
#include "mqtt_client.h"
#include "adc_sampler.h"
#include "pwm_control.h"
#include <stdio.h>

// Configuration - update these for your setup
#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"
#define MQTT_BROKER_IP "192.168.1.100"
#define MQTT_BROKER_PORT 1883
#define DEVICE_ID "bike1"

// Sampling configuration
#define ADC_SAMPLE_RATE_HZ 100    // Sample ADC at 100 Hz
#define MQTT_PUBLISH_RATE_HZ 10   // Publish at 10 Hz
#define PWM_GPIO_PIN 15           // GPIO pin for PWM control

static uint32_t sequence_number = 0;

int main() {
    stdio_init_all();
    
    printf("\n=== Pedal Power Firmware Starting ===\n");
    
    // Initialize WiFi
    if (cyw43_arch_init()) {
        printf("Failed to initialize WiFi\n");
        return 1;
    }
    
    cyw43_arch_enable_sta_mode();
    
    printf("Connecting to WiFi...\n");
    if (cyw43_arch_wifi_connect_timeout_ms(WIFI_SSID, WIFI_PASSWORD, 
                                            CYW43_AUTH_WPA2_AES_PSK, 30000)) {
        printf("Failed to connect to WiFi\n");
        return 1;
    }
    
    printf("WiFi connected\n");
    
    // Initialize MQTT client
    printf("Connecting to MQTT broker at %s:%d\n", MQTT_BROKER_IP, MQTT_BROKER_PORT);
    if (!mqtt_client_init(MQTT_BROKER_IP, MQTT_BROKER_PORT)) {
        printf("Failed to initialize MQTT client\n");
        return 1;
    }
    
    // Wait for MQTT connection
    printf("Waiting for MQTT connection...\n");
    int timeout = 100; // 10 seconds
    while (!mqtt_is_connected() && timeout-- > 0) {
        sleep_ms(100);
        cyw43_arch_poll();
    }
    
    if (!mqtt_is_connected()) {
        printf("MQTT connection timeout\n");
        return 1;
    }
    
    printf("MQTT connected\n");
    
    // Initialize ADC sampler
    adc_sampler_init(ADC_SAMPLE_RATE_HZ);
    
    // Initialize PWM control
    pwm_control_init(PWM_GPIO_PIN);
    
    printf("=== Firmware Initialized ===\n");
    printf("ADC sampling at %d Hz\n", ADC_SAMPLE_RATE_HZ);
    printf("MQTT publishing at %d Hz\n", MQTT_PUBLISH_RATE_HZ);
    
    // Main loop
    uint32_t publish_interval_ms = 1000 / MQTT_PUBLISH_RATE_HZ;
    absolute_time_t next_publish = make_timeout_time_ms(publish_interval_ms);
    
    while (true) {
        // Keep WiFi and MQTT running
        cyw43_arch_poll();
        
        // Publish telemetry at configured rate
        if (time_reached(next_publish)) {
            float voltage, current, power;
            adc_get_readings(&voltage, &current, &power);
            
            if (mqtt_is_connected()) {
                if (mqtt_publish_telemetry(DEVICE_ID, sequence_number, 
                                            voltage, current, power)) {
                    sequence_number++;
                    
                    // Blink LED on successful publish
                    cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 1);
                    sleep_ms(50);
                    cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 0);
                }
            } else {
                printf("MQTT disconnected, attempting reconnect...\n");
                mqtt_client_init(MQTT_BROKER_IP, MQTT_BROKER_PORT);
            }
            
            next_publish = make_timeout_time_ms(publish_interval_ms);
        }
        
        sleep_ms(10); // Small delay to prevent tight loop
    }
    
    return 0;
}
