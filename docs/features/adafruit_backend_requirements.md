# Adafruit CircuitPython NeoPixel SPI Backend Requirements

## Overview

The Adafruit CircuitPython NeoPixel SPI backend provides Raspberry Pi 5 support by using the SPI interface instead of PWM. This is the recommended approach for Pi 5 because it doesn't require firmware updates and is more stable.

## Why SPI for Raspberry Pi 5?

The Raspberry Pi 5 uses the RP1 chip for peripheral IO, which made existing libraries like `rpi_ws281x` stop working. There are two options for NeoPixels on Pi 5:

1. **SPI-based (Recommended)**: Uses `adafruit-circuitpython-neopixel-spi` - simpler, no firmware updates required
2. **PIO-based**: Uses `Adafruit-Blinka-Raspberry-Pi5-Neopixel` - requires firmware updates, less tested

This plugin uses the **SPI-based approach** for maximum stability and compatibility.

## Python Package Requirements

### Automatic Installation (Recommended)

**When installing or updating this plugin via OctoPrint's Plugin Manager, all required dependencies are installed automatically.** This includes both:
- `rpi_ws281x>=4.3.3` (for Pi 1-4 PWM backend)
- `adafruit-circuitpython-neopixel-spi>=1.0.0` (for Pi 5 SPI backend)

**No manual pip installation is required!**

### Manual Installation (Advanced/Development Only)

If you're installing the plugin manually or developing locally, install the Adafruit backend dependencies:

```bash
pip3 install adafruit-circuitpython-neopixel-spi
```

This package automatically installs its dependencies:
- `adafruit-circuitpython-busdevice`
- `adafruit-circuitpython-pixelbuf`
- `Adafruit-Blinka` (provides CircuitPython compatibility on Linux)

## System Requirements

### Hardware Requirements
- Raspberry Pi 5 (or other models with SPI support)
- NeoPixel/WS281x compatible LED strip

### GPIO Pin Requirements

**CRITICAL:** The SPI-based approach **MUST** use the SPI MOSI pin:
- **Raspberry Pi 5/4/3/Zero 2**: GPIO 10 (Physical pin 19)
- **Raspberry Pi 1/Zero**: GPIO 10 (Physical pin 19)

Unlike `rpi_ws281x` which supports multiple GPIO pins, the SPI backend is restricted to the hardware SPI MOSI pin. **Pin configuration is not user-selectable when using this backend.**

### SPI Configuration

1. **Enable SPI interface:**
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options -> SPI -> Enable
   ```

2. **Verify SPI is enabled:**
   ```bash
   ls -l /dev/spidev0.*
   ```
   Should show `/dev/spidev0.0` and `/dev/spidev0.1`

3. **User permissions:**
   The user running OctoPrint must be in the `spi` group:
   ```bash
   sudo usermod -a -G spi $USER
   ```
   Log out and back in for changes to take effect.

### System Dependencies

Ensure system packages are up to date:
```bash
sudo apt update
sudo apt install python3-dev python3-pip
```

## API Differences from rpi_ws281x

### Initialization

**rpi_ws281x:**
```python
strip = PixelStrip(num_pixels, pin, freq_hz, dma, invert, brightness, channel, strip_type)
```

**neopixel_spi:**
```python
import board
pixels = neopixel_spi.NeoPixel_SPI(board.SPI(), num_pixels, pixel_order=neopixel_spi.GRB, auto_write=False)
```

### Key Differences

1. **Pin Configuration**: Cannot be configured - always uses SPI MOSI (GPIO 10)
2. **Frequency**: Automatically handled by SPI hardware
3. **DMA**: Not applicable (SPI uses different hardware)
4. **Channel**: Not applicable
5. **Pixel Order**: Uses `pixel_order` parameter instead of `strip_type`
6. **Brightness**: Handled at pixelbuf level, not hardware level

### Pixel Order Mapping

Map `rpi_ws281x` strip types to `neopixel_spi` pixel orders:

| rpi_ws281x strip_type | neopixel_spi pixel_order |
|-----------------------|--------------------------|
| WS2811_STRIP_RGB      | RGB                      |
| WS2811_STRIP_RBG      | RBG                      |
| WS2811_STRIP_GRB      | GRB                      |
| WS2811_STRIP_GBR      | GBR                      |
| WS2811_STRIP_BRG      | BRG                      |
| WS2811_STRIP_BGR      | BGR                      |
| SK6812_STRIP_RGBW     | RGBW                     |
| SK6812_STRIP_RBGW     | RBGW                     |
| SK6812_STRIP_GRBW     | GRBW                     |
| SK6812_STRIP_GBRW     | GBRW                     |
| SK6812_STRIP_BRGW     | BRGW                     |
| SK6812_STRIP_BGRW     | BGRW                     |

## Backend Availability Detection

The backend should be considered available if:

1. **Python package check:**
   ```python
   try:
       import neopixel_spi
       import board
       backend_available = True
   except ImportError:
       backend_available = False
   ```

2. **SPI device check:**
   ```python
   import os
   spi_available = os.path.exists('/dev/spidev0.0')
   ```

3. **Permission check:**
   ```python
   import os
   spi_writable = os.access('/dev/spidev0.0', os.W_OK)
   ```

All three conditions should be met for the backend to be considered fully available.

## Configuration Parameters

### Backend Configuration Schema

```python
{
    "type": "adafruit_neopixel_spi",
    "config": {
        "count": 24,                    # Number of LEDs
        "brightness": 50,                # 0-100 percentage
        "pixel_order": "GRB",           # RGB, GRB, RGBW, GRBW, etc.
        "auto_write": False,            # Buffer writes (should be False)
        # Note: pin, freq_hz, dma, channel, invert are NOT applicable
    }
}
```

### Parameters Not Used by This Backend

The following parameters from `rpi_ws281x` are **ignored** by the Adafruit backend:
- `pin` - Always GPIO 10 (MOSI)
- `freq_hz` - Determined by SPI hardware
- `dma` - Not applicable to SPI
- `channel` - Not applicable to SPI
- `invert` - Not supported

## Behavioral Differences

### Brightness Control

- **rpi_ws281x**: Hardware PWM brightness control (0-255)
- **neopixel_spi**: Software brightness at pixelbuf level

The plugin should apply brightness adjustments at the color level before sending to the backend.

### Performance

- **rpi_ws281x**: Very fast, hardware-controlled timing
- **neopixel_spi**: Slightly slower due to SPI overhead, but still sufficient for smooth animations

### Compatibility

- **rpi_ws281x**: Pi 1-4, Zero, Zero 2 (not Pi 5)
- **neopixel_spi**: All Raspberry Pi models with SPI, including Pi 5

## User Setup Guide

### Quick Start for Pi 5 Users

**Note:** When you install or update this plugin via OctoPrint's Plugin Manager, the Adafruit backend dependencies are installed automatically. You only need to configure the system.

1. Enable SPI:
   ```bash
   sudo raspi-config
   # Interface Options -> SPI -> Yes
   ```

2. Add user to SPI group:
   ```bash
   sudo usermod -a -G spi pi
   ```

3. Connect LED strip to:
   - Data: GPIO 10 (Physical pin 19)
   - Power: 5V (Physical pin 2 or 4)
   - Ground: GND (Physical pin 6, 9, 14, 20, 25, 30, 34, or 39)

4. Select "Adafruit NeoPixel (SPI)" backend in plugin settings

5. Restart OctoPrint

### Troubleshooting

**"No module named 'neopixel_spi'"**
- If you installed the plugin via OctoPrint's Plugin Manager, the dependencies should be installed automatically
- Try reinstalling or updating the plugin via Plugin Manager
- For manual installations: `~/oprint/bin/pip install adafruit-circuitpython-neopixel-spi`

**"Permission denied: /dev/spidev0.0"**
- Add user to spi group: `sudo usermod -a -G spi $USER`
- Log out and back in

**"SPI device not found"**
- Enable SPI in raspi-config
- Reboot after enabling

**LEDs not lighting up**
- Verify GPIO 10 connection (MUST use pin 19)
- Check pixel order matches your LED strip (try GRB if unsure)
- Verify 5V power connection
- Test strip with a simple standalone script first

## Implementation Notes for Backend

### Color Format

The Adafruit library expects colors as integers in the format 0xRRGGBB (or 0xWWRRGGBB for RGBW). This matches the plugin's internal color format, so no conversion is needed.

### Brightness Handling

Since the Adafruit library handles brightness at the pixelbuf level, the backend should:
1. Accept brightness as percentage (0-100)
2. Apply brightness by scaling color values before setting pixels
3. Store current brightness for `get_brightness()` calls

### Auto-Write Parameter

The backend should initialize with `auto_write=False` to allow buffering pixel updates and only writing when `show()` is called. This matches the plugin's existing behavior.

## References

- [Adafruit NeoPixel SPI GitHub](https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel_SPI)
- [Adafruit CircuitPython NeoPixel SPI Documentation](https://docs.circuitpython.org/projects/neopixel_spi/en/latest/)
- [Using NeoPixels on Pi 5](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/using-neopixels-on-the-pi-5)
- [NeoPixels on Raspberry Pi Guide](https://learn.adafruit.com/neopixels-on-raspberry-pi)
