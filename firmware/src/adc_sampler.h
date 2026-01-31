#ifndef ADC_SAMPLER_H
#define ADC_SAMPLER_H

#include <stdint.h>
#include <stdbool.h>

// Initialize ADC sampler with sampling rate
void adc_sampler_init(uint32_t sample_rate_hz);

// Get latest voltage, current, and power readings
void adc_get_readings(float *voltage, float *current, float *power);

#endif // ADC_SAMPLER_H
