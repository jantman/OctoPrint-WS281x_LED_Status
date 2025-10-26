# Raspberry Pi 5 Support Guide

This plugin now supports **Raspberry Pi 5** through multiple LED control backends! Choose the backend that works best for your hardware.

## Quick Start for Raspberry Pi 5 Users

**Recommended Setup:**
1. Use the **Adafruit NeoPixel (SPI)** backend
2. Connect LED strip data wire to **GPIO 10** (Physical pin 19)
3. Enable SPI and install dependencies (see below)
4. Select backend in plugin settings

---

## LED Control Backends

### What is a Backend?

A backend is the software library that controls your LED strip. Different Raspberry Pi models require different approaches due to hardware changes.

### Available Backends

#### 1. rpi_ws281x (PWM) - **For Pi 1-4, Zero**
- **Works on:** Raspberry Pi 1, 2, 3, 4, Zero, Zero 2
- **Does NOT work on:** Raspberry Pi 5
- **Interface:** PWM/PCM
- **GPIO pins:** 10, 12, 18, or 21 (configurable)
- **Setup:** Add user to `gpio` group
- **Status:** Default for existing installations

**Pros:**
- Well-established and tested
- Hardware-based timing
- Multiple GPIO pin options
- Fast and reliable

**Cons:**
- Incompatible with Raspberry Pi 5
- Requires specific GPIO pins

#### 2. Adafruit NeoPixel (SPI) - **For Pi 5 (and all models)**
- **Works on:** All Raspberry Pi models including Pi 5
- **Interface:** SPI
- **GPIO pin:** GPIO 10 only (Physical pin 19) - not configurable
- **Setup:** Enable SPI, add user to `spi` group
- **Status:** Recommended for Pi 5 users

**Pros:**
- **Works on Raspberry Pi 5**
- No firmware updates required
- Works on all Pi models
- Simple SPI-based communication

**Cons:**
- Must use GPIO 10 (SPI MOSI pin)
- Slightly slower than PWM (but still very fast)
- Requires SPI to be enabled

---

## Setup Instructions

### For Raspberry Pi 5 Users

#### Step 1: Enable SPI

```bash
sudo raspi-config
```

Navigate to: **Interface Options → SPI → Yes**

Reboot when prompted, or manually:
```bash
sudo reboot
```

#### Step 2: Verify SPI is Enabled

```bash
ls -l /dev/spidev0.*
```

You should see `/dev/spidev0.0` and `/dev/spidev0.1`

#### Step 3: Add User to SPI Group

```bash
sudo usermod -a -G spi pi
```

**Important:** Log out and back in (or reboot) for group changes to take effect.

#### Step 4: Install Adafruit Dependencies

If using OctoPrint's virtual environment (recommended):

```bash
~/oprint/bin/pip install adafruit-circuitpython-neopixel-spi
```

If using system Python:

```bash
pip3 install adafruit-circuitpython-neopixel-spi
```

#### Step 5: Connect LED Strip

- **Data wire:** GPIO 10 (Physical pin 19)
- **Power (5V):** Physical pin 2 or 4
- **Ground:** Physical pin 6, 9, 14, 20, 25, 30, 34, or 39

**Important:** GPIO 10 is required for SPI. Other pins will not work with this backend.

#### Step 6: Configure Plugin

1. Open OctoPrint Settings
2. Navigate to: **Plugins → WS281x LED Status**
3. Click "LED Strip settings" button
4. In "Backend Type" dropdown, select **"Adafruit NeoPixel (SPI)"**
5. Set "Number of LEDs" to match your strip
6. Set "Pixel Order":
   - Most NeoPixels use **GRB**
   - Try RGB if colors are wrong
   - Use RGBW/GRBW for strips with white LEDs
7. Set "Max Brightness" (start with 50%)
8. Click "Close" then "Save" in main settings
9. Restart OctoPrint

#### Step 7: Test Your Setup

1. Go to the plugin's "Overview" tab
2. Test effects to verify LEDs work correctly
3. If colors are wrong, try different pixel orders

---

### For Raspberry Pi 1-4 Users

**Good news:** Your existing setup continues to work! The plugin defaults to the **rpi_ws281x (PWM)** backend for backward compatibility.

**If you want to try the Adafruit backend:**
- Follow the same setup instructions as Pi 5 users
- Remember: You must use GPIO 10 with the Adafruit backend
- Your current GPIO pin configuration won't work if it's not GPIO 10

---

## Troubleshooting

### Adafruit Backend Issues

#### "No module named 'neopixel_spi'"

**Solution:** Install the Adafruit library:
```bash
~/oprint/bin/pip install adafruit-circuitpython-neopixel-spi
```

#### "Permission denied: /dev/spidev0.0"

**Solution:** Add user to SPI group and log out/in:
```bash
sudo usermod -a -G spi $USER
# Log out and back in, or reboot
```

#### "SPI device not found"

**Solution:** Enable SPI in raspi-config:
```bash
sudo raspi-config
# Interface Options → SPI → Yes
sudo reboot
```

#### LEDs Not Lighting Up

**Checklist:**
1. ✓ GPIO 10 connected (Physical pin 19) - **Must use this pin!**
2. ✓ Pixel order matches your strip (try GRB first, then RGB)
3. ✓ 5V power connected to LEDs
4. ✓ Ground shared between Pi and LED power supply
5. ✓ SPI enabled and permissions correct
6. ✓ Correct number of LEDs configured

**Test with simple script:**
```python
import board
import neopixel_spi

pixels = neopixel_spi.NeoPixel_SPI(board.SPI(), 24, pixel_order=(1, 0, 2), brightness=0.5, auto_write=False)
pixels.fill(0x00FF00)  # Green
pixels.show()
```

#### Wrong Colors

**Solution:** Try different pixel orders in this order:
1. **GRB** (most common for NeoPixels)
2. **RGB** (common for some strips)
3. **RGBW** (if your strip has white LEDs)
4. **GRBW** (RGBW alternative)

### rpi_ws281x Backend Issues

#### "Library not found" or Import Errors

**Solution:** Install rpi_ws281x:
```bash
~/oprint/bin/pip install rpi-ws281x
```

#### "Permission denied" or "Can't open /dev/mem"

**Solution:** Add user to gpio group:
```bash
sudo usermod -a -G gpio $USER
# Log out and back in
```

#### LEDs Not Working on Pi 5

**Solution:** The rpi_ws281x backend **does not work on Raspberry Pi 5**. Use the Adafruit backend instead.

---

## Backend Comparison

| Feature | rpi_ws281x (PWM) | Adafruit (SPI) |
|---------|------------------|----------------|
| **Pi 5 Support** | ❌ No | ✅ Yes |
| **Pi 1-4 Support** | ✅ Yes | ✅ Yes |
| **GPIO Pins** | 10, 12, 18, 21 | 10 only |
| **Speed** | Fastest | Very fast |
| **Setup Complexity** | Easy | Easy |
| **Firmware Updates** | None | None |
| **Permissions** | gpio group | spi group |
| **Interface** | PWM/PCM | SPI |

---

## Switching Backends

You can switch backends at any time in the plugin settings:

1. Open **Settings → WS281x LED Status**
2. Click **"LED Strip settings"**
3. Change **"Backend Type"** dropdown
4. Update settings for new backend (GPIO pin, pixel order, etc.)
5. **Save settings**
6. **Restart OctoPrint**

**Important:** Changing backends requires OctoPrint restart to take effect.

---

## Pixel Order Reference

Different LED strips use different color orders. If your colors are wrong, try these:

### RGB Strips (3 colors)
- **GRB** - Most NeoPixels (WS2812, WS2812B)
- **RGB** - Some generic strips
- **RBG, GBR, BRG, BGR** - Less common

### RGBW Strips (4 colors with white)
- **GRBW** - Most RGBW NeoPixels (SK6812)
- **RGBW** - Some RGBW strips
- **RBGW, GBRW, BRGW, BGRW** - Other variations

**Tip:** If unsure, try GRB first (most common), then RGB.

---

## Hardware Pinout Reference

### Raspberry Pi 5 GPIO 10 (SPI MOSI)
```
Physical Pin 19 = GPIO 10 = SPI MOSI
```

### Complete Pinout for LED Connection
```
Pin 2 or 4:  5V Power (if powering small strips)
Pin 19:      GPIO 10 (Data) - SPI MOSI - REQUIRED for Adafruit backend
Pin 6,9,14,
20,25,30,
34,or 39:    Ground
```

**Power Warning:** Only power small LED strips (< 10 LEDs) from Pi's 5V pins. Larger strips need external power supply with shared ground.

---

## FAQ

### Q: Can I use the Adafruit backend on Raspberry Pi 4?
**A:** Yes! The Adafruit backend works on all Pi models, but you must use GPIO 10.

### Q: Why can't I configure the GPIO pin with Adafruit backend?
**A:** The Adafruit backend uses the hardware SPI interface, which is fixed to GPIO 10 (MOSI pin). This is a hardware limitation.

### Q: Will my existing setup continue working?
**A:** Yes! The plugin automatically uses the rpi_ws281x backend by default for backward compatibility. Pi 1-4 users don't need to change anything.

### Q: Can I switch back to rpi_ws281x after trying Adafruit?
**A:** Yes! Just change the backend in settings and restart OctoPrint. Your settings are preserved.

### Q: What if I'm using GPIO 18 with rpi_ws281x?
**A:** If you switch to Adafruit backend, you'll need to move your data wire to GPIO 10. The rpi_ws281x backend will continue to work on GPIO 18 on Pi 1-4.

### Q: Do both backends support all plugin features?
**A:** Yes! Both backends support all effects, color correction, progress bars, and every plugin feature. They're fully compatible.

### Q: Which backend is faster?
**A:** rpi_ws281x is slightly faster due to hardware PWM, but the Adafruit backend is still very fast. You won't notice a difference in normal use.

### Q: Can I use RGBW strips with the Adafruit backend?
**A:** Yes! The Adafruit backend fully supports RGBW strips. Select the appropriate pixel order (RGBW, GRBW, etc.) in settings.

---

## Additional Resources

- [Plugin Documentation](https://cp2004.gitbook.io/ws281x-led-status/)
- [Adafruit NeoPixel SPI Library](https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel_SPI)
- [Raspberry Pi GPIO Pinout](https://pinout.xyz/)
- [NeoPixel Überguide](https://learn.adafruit.com/adafruit-neopixel-uberguide)

---

## Support

If you encounter issues:

1. Check the [troubleshooting section](#troubleshooting) above
2. Enable debug logging in plugin settings
3. Check OctoPrint logs for error messages
4. Report issues on [GitHub](https://github.com/cp2004/OctoPrint-WS281x_LED_Status/issues)

When reporting issues, please include:
- Raspberry Pi model
- Backend being used
- LED strip type and count
- GPIO pin connected
- Relevant error messages from logs
