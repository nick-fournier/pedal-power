#include "pwm_control.h"
#include "hardware/pwm.h"
#include "hardware/gpio.h"
#include <stdio.h>

#define PWM_FREQ_HZ 25000  // 25 kHz PWM frequency

static uint pwm_slice;
static uint pwm_channel;

void pwm_control_init(uint gpio_pin) {
    // Set up PWM on the specified GPIO pin
    gpio_set_function(gpio_pin, GPIO_FUNC_PWM);
    
    pwm_slice = pwm_gpio_to_slice_num(gpio_pin);
    pwm_channel = pwm_gpio_to_channel(gpio_pin);
    
    // Configure PWM
    pwm_config config = pwm_get_default_config();
    
    // Set PWM frequency
    // System clock is 125 MHz
    // divider = 125MHz / (PWM_FREQ * 65536) 
    // For simplicity, use wrap value to set frequency
    uint32_t clock_freq = 125000000;
    uint32_t divider = 1;
    uint32_t wrap = clock_freq / (divider * PWM_FREQ_HZ);
    
    pwm_config_set_clkdiv(&config, divider);
    pwm_config_set_wrap(&config, wrap - 1);
    
    pwm_init(pwm_slice, &config, true);
    
    // Start with 0% duty cycle
    pwm_set_duty_cycle(0);
    
    printf("PWM initialized on GPIO %d at %d Hz\n", gpio_pin, PWM_FREQ_HZ);
}

void pwm_set_duty_cycle(uint8_t duty_percent) {
    if (duty_percent > 100) {
        duty_percent = 100;
    }
    
    uint16_t wrap = pwm_get_wrap(pwm_slice);
    uint16_t level = (wrap * duty_percent) / 100;
    
    pwm_set_chan_level(pwm_slice, pwm_channel, level);
}
