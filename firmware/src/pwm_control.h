#ifndef PWM_CONTROL_H
#define PWM_CONTROL_H

#include <stdint.h>

// Initialize PWM for local control
void pwm_control_init(uint gpio_pin);

// Set PWM duty cycle (0-100%)
void pwm_set_duty_cycle(uint8_t duty_percent);

#endif // PWM_CONTROL_H
