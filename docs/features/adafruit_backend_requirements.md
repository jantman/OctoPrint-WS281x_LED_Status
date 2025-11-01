# Adafruit CircuitPython NeoPixel (PWM) Backend Requirements

## Overview

The Adafruit CircuitPython NeoPixel (PWM) backend provides Raspberry Pi 5 support by using the PWM interface. This backend also works on all older Raspberry Pi models, providing a consistent alternative to the `rpi_ws281x` library.

## Why PWM for Raspberry Pi 5?

The Raspberry Pi 5 uses the RP1 chip for peripheral IO, which made existing libraries like `rpi_ws281x` stop working. The Adafruit CircuitPython NeoPixel library provides a stable, well-maintained solution that works across all Raspberry Pi models including Pi 5.

Key advantages:
- **Works on all Pi models** (Pi 1-5, Zero, Zero 2)
- **Flexible GPIO pin selection** - Use any GPIO pin, not restricted to specific pins
- **No special configuration required** - No need to enable SPI or modify system files
- **Simple user permissions** - Only requires standard GPIO access

## Python Package Requirements

### Automatic Installation (Recommended)

**When installing or updating this plugin via OctoPrint's Plugin Manager, all required dependencies are installed automatically.** This includes both:
- `rpi_ws281x>=4.3.3` (for Pi 1-4 PWM backend)
- `adafruit-circuitpython-neopixel>=1.0.0` (for Pi 5 PWM backend)

**No manual pip installation is required!**

### Manual Installation (Advanced/Development Only)

If you're installing the plugin manually or developing locally, install the Adafruit backend dependencies:

```bash
pip3 install adafruit-circuitpython-neopixel
```

This package automatically installs its dependencies:
- `adafruit-circuitpython-pixelbuf`
- `Adafruit-Blinka` (provides CircuitPython compatibility on Linux)

## System Requirements

### Hardware Requirements
- Raspberry Pi (any model: 1-5, Zero, Zero 2)
- NeoPixel/WS281x compatible LED strip

### GPIO Pin Requirements

**Flexible Pin Selection:** Unlike the older SPI-based approach, the PWM backend supports **any GPIO pin**. Common choices:
- **GPIO 10** (Physical pin 19) - SPI MOSI, good default
- **GPIO 18** (Physical pin 12) - PWM-capable, popular choice
- **GPIO 21** (Physical pin 40) - PWM-capable

You can configure your preferred GPIO pin in the plugin settings.

### User Permissions

The user running OctoPrint only needs standard GPIO access - no special group membership required. If you encounter permission issues, ensure your user has GPIO access (most Pi users do by default).

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

**neopixel (PWM):**
```python
import board
from neopixel import NeoPixel
pixels = NeoPixel(board.D18, num_pixels, brightness=0.5, auto_write=False, pixel_order=neopixel.GRB)
```

### Key Differences

1. **Pin Configuration**: User-configurable - supports any GPIO pin via `board.D{pin}`
2. **Frequency**: Automatically handled by PWM hardware
3. **DMA**: Not applicable (PWM uses different hardware)
4. **Channel**: Not applicable
5. **Pixel Order**: Uses `pixel_order` parameter instead of `strip_type`
6. **Brightness**: Float 0.0-1.0 instead of integer 0-255

### Pixel Order Mapping

Map `rpi_ws281x` strip types to `neopixel` pixel orders:

| rpi_ws281x strip_type | neopixel pixel_order |
|-----------------------|----------------------|
| WS2811_STRIP_RGB      | RGB                  |
| WS2811_STRIP_RBG      | RBG                  |
| WS2811_STRIP_GRB      | GRB                  |
| WS2811_STRIP_GBR      | GBR                  |
| WS2811_STRIP_BRG      | BRG                  |
| WS2811_STRIP_BGR      | BGR                  |
| SK6812_STRIP_RGBW     | RGBW                 |
| SK6812_STRIP_RBGW     | RBGW                 |
| SK6812_STRIP_GRBW     | GRBW                 |
| SK6812_STRIP_GBRW     | GBRW                 |
| SK6812_STRIP_BRGW     | BRGW                 |
| SK6812_STRIP_BGRW     | BGRW                 |

## Backend Availability Detection

The backend should be considered available if the Python packages are installed:

```python
try:
    import neopixel
    import board
    backend_available = True
except ImportError:
    backend_available = False
```

No device or permission checks are required beyond basic GPIO access.

## Configuration Parameters

### Backend Configuration Schema

```python
{
    "type": "adafruit_neopixel_pwm",
    "config": {
        "count": 24,                    # Number of LEDs
        "pin": 18,                      # GPIO pin number (0-27)
        "brightness": 50,               # 0-100 percentage
        "pixel_order": "GRB",           # RGB, GRB, RGBW, GRBW, etc.
        "auto_write": False,            # Buffer writes (should be False)
        # Note: freq_hz, dma, channel, invert are NOT applicable
    }
}
```

### Parameters Not Used by This Backend

The following parameters from `rpi_ws281x` are **ignored** by the Adafruit PWM backend:
- `freq_hz` - Determined by PWM hardware
- `dma` - Not applicable to PWM
- `channel` - Not applicable to PWM
- `invert` - Not supported

### New Parameters

- `pin` (int, required): GPIO pin number (0-27)
  - Common choices: 10, 18, 21
  - Configurable in plugin settings

## Behavioral Differences

### Brightness Control

- **rpi_ws281x**: Hardware PWM brightness control (0-255)
- **neopixel**: Software brightness at pixel level (0.0-1.0)

The plugin converts percentage (0-100) to float (0.0-1.0) for the backend.

### Performance

- **rpi_ws281x**: Very fast, hardware-controlled timing
- **neopixel PWM**: Similar performance, sufficient for smooth animations

### Compatibility

- **rpi_ws281x**: Pi 1-4, Zero, Zero 2 (not Pi 5)
- **neopixel PWM**: All Raspberry Pi models (Pi 1-5, Zero, Zero 2)

## User Setup Guide

### Quick Start for Pi 5 Users

**Note:** When you install or update this plugin via OctoPrint's Plugin Manager, the Adafruit backend dependencies are installed automatically.

1. Connect LED strip to your chosen GPIO pin:
   - Data: GPIO 18 (Physical pin 12) - recommended default
   - Power: 5V (Physical pin 2 or 4)
   - Ground: GND (Physical pin 6, 9, 14, 20, 25, 30, 34, or 39)

2. In plugin settings:
   - Select "Adafruit CircuitPython NeoPixel (PWM)" backend
   - Configure GPIO pin (default: 18)
   - Configure pixel order (most NeoPixels use GRB)

3. Restart OctoPrint

That's it! No system configuration or user group changes required.

### Troubleshooting

**"No module named 'neopixel'"**
- If you installed the plugin via OctoPrint's Plugin Manager, the dependencies should be installed automatically
- Try reinstalling or updating the plugin via Plugin Manager
- For manual installations: `~/oprint/bin/pip install adafruit-circuitpython-neopixel`

**"Invalid GPIO pin number"**
- Ensure pin number is between 0-27
- Try common pins: 10, 18, or 21
- Verify your Pi model supports the pin you're trying to use

**"GPIO pin X not available on this board"**
- The requested GPIO pin doesn't exist on your Pi model
- Try GPIO 10, 18, or 21 (available on all Pi models)

**LEDs not lighting up**
- Verify data wire connection to your configured GPIO pin
- Check pixel order matches your LED strip (try GRB if unsure)
- Verify 5V power connection
- Test strip with a simple standalone script first

## Implementation Notes for Backend

### Color Format

Colors should be provided as tuples: `(r, g, b)` or `(r, g, b, w)` with values 0-255. The Adafruit library handles these natively.

### Brightness Handling

The backend should:
1. Accept brightness as percentage (0-100)
2. Convert to float (0.0-1.0) for the NeoPixel library
3. Store current brightness for `get_brightness()` calls

### Auto-Write Parameter

The backend should initialize with `auto_write=False` to allow buffering pixel updates and only writing when `show()` is called. This matches the plugin's existing behavior.

### GPIO Pin Access

The backend uses `board.D{pin}` notation to access GPIO pins. For example, GPIO 18 is accessed as `board.D18`.

## References

- [Adafruit CircuitPython NeoPixel GitHub](https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel)
- [Adafruit CircuitPython NeoPixel Documentation](https://docs.circuitpython.org/projects/neopixel/en/latest/)
- [NeoPixels on Raspberry Pi Guide](https://learn.adafruit.com/neopixels-on-raspberry-pi)
- [CircuitPython on Raspberry Pi Linux](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux)
