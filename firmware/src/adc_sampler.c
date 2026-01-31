#include "adc_sampler.h"
#include "hardware/adc.h"
#include "hardware/timer.h"
#include "pico/stdlib.h"
#include <stdio.h>

#define ADC_VOLTAGE_CHANNEL 0  // ADC0 (GPIO26)
#define ADC_CURRENT_CHANNEL 1  // ADC1 (GPIO27)
#define ADC_VREF 3.3f
#define ADC_MAX_VALUE 4095.0f  // 12-bit ADC

// Voltage divider ratio (adjust based on hardware)
#define VOLTAGE_SCALE 11.0f  // For 0-36V range
#define CURRENT_SCALE 10.0f  // For 0-10A range (using current sensor)

static volatile float latest_voltage = 0.0f;
static volatile float latest_current = 0.0f;
static volatile float latest_power = 0.0f;
static volatile uint32_t sample_count = 0;

// Moving average for smoothing
#define AVG_SAMPLES 10
static float voltage_buffer[AVG_SAMPLES] = {0};
static float current_buffer[AVG_SAMPLES] = {0};
static uint32_t buffer_index = 0;

static repeating_timer_t sampling_timer;

// Timer callback for ADC sampling
static bool adc_sample_callback(repeating_timer_t *rt) {
    // Read voltage (ADC0)
    adc_select_input(ADC_VOLTAGE_CHANNEL);
    uint16_t raw_voltage = adc_read();
    float voltage = (raw_voltage / ADC_MAX_VALUE) * ADC_VREF * VOLTAGE_SCALE;
    
    // Read current (ADC1)
    adc_select_input(ADC_CURRENT_CHANNEL);
    uint16_t raw_current = adc_read();
    float current = (raw_current / ADC_MAX_VALUE) * ADC_VREF * CURRENT_SCALE;
    
    // Update buffers
    voltage_buffer[buffer_index] = voltage;
    current_buffer[buffer_index] = current;
    buffer_index = (buffer_index + 1) % AVG_SAMPLES;
    
    // Calculate moving averages
    float avg_voltage = 0.0f;
    float avg_current = 0.0f;
    for (int i = 0; i < AVG_SAMPLES; i++) {
        avg_voltage += voltage_buffer[i];
        avg_current += current_buffer[i];
    }
    avg_voltage /= AVG_SAMPLES;
    avg_current /= AVG_SAMPLES;
    
    // Update latest readings
    latest_voltage = avg_voltage;
    latest_current = avg_current;
    latest_power = avg_voltage * avg_current;
    sample_count++;
    
    return true; // Continue repeating
}

void adc_sampler_init(uint32_t sample_rate_hz) {
    // Initialize ADC
    adc_init();
    adc_gpio_init(26); // ADC0
    adc_gpio_init(27); // ADC1
    adc_set_temp_sensor_enabled(false);
    
    // Set up sampling timer (negative for microseconds)
    int32_t delay_us = -(1000000 / sample_rate_hz);
    add_repeating_timer_us(delay_us, adc_sample_callback, NULL, &sampling_timer);
    
    printf("ADC sampler initialized at %lu Hz\n", (unsigned long)sample_rate_hz);
}

void adc_get_readings(float *voltage, float *current, float *power) {
    if (voltage) *voltage = latest_voltage;
    if (current) *current = latest_current;
    if (power) *power = latest_power;
}
