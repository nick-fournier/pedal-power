cmake_minimum_required(VERSION 3.13)

# Pull in SDK (must be before project)
include(pico_sdk_import.cmake)

project(pedal_power_firmware C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Initialize the SDK
pico_sdk_init()

add_executable(pedal_power
    src/main.c
    src/mqtt_client.c
    src/adc_sampler.c
    src/pwm_control.c
)

# Pull in common dependencies
target_link_libraries(pedal_power
    pico_stdlib
    pico_cyw43_arch_lwip_threadsafe_background
    pico_lwip_mqtt
    hardware_adc
    hardware_pwm
)

# Enable USB output, disable UART output
pico_enable_stdio_usb(pedal_power 1)
pico_enable_stdio_uart(pedal_power 0)

# Create map/bin/hex/uf2 files
pico_add_extra_outputs(pedal_power)
