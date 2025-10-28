__author__ = "Jason Antman <jason@jasonantman.com>"
__license__ = "GNU Affero General Public License http://www.gnu.org/licenses/agpl.html"
__copyright__ = "Copyright (c) Jason Antman 2025 - released under the terms of the AGPLv3 License"

"""
Adafruit CircuitPython NeoPixel PWM backend for LED control.

This backend uses the adafruit-circuitpython-neopixel library to control
NeoPixel LEDs via the PWM interface. This approach works on all Raspberry Pi
models including the Raspberry Pi 5.

Key features:
- Works on all Raspberry Pi models (1-5)
- Supports any GPIO pin (configurable)
- Supports RGB and RGBW pixel orders
- Software-based brightness control
- No special group membership or configuration required
"""

from typing import Any, Dict, Tuple

from octoprint_ws281x_led_status.backend import LEDBackend

# Try to import Adafruit libraries - they may not be installed
try:
    import board
    from neopixel import NeoPixel
    import neopixel

    ADAFRUIT_AVAILABLE = True
except ImportError:
    ADAFRUIT_AVAILABLE = False


# Pixel order constants mapping to neopixel library constants
PIXEL_ORDERS = {
    # RGB variations
    "RGB": neopixel.RGB if ADAFRUIT_AVAILABLE else None,
    "RBG": neopixel.RBG if ADAFRUIT_AVAILABLE else None,
    "GRB": neopixel.GRB if ADAFRUIT_AVAILABLE else None,
    "GBR": neopixel.GBR if ADAFRUIT_AVAILABLE else None,
    "BRG": neopixel.BRG if ADAFRUIT_AVAILABLE else None,
    "BGR": neopixel.BGR if ADAFRUIT_AVAILABLE else None,
    # RGBW variations
    "RGBW": neopixel.RGBW if ADAFRUIT_AVAILABLE else None,
    "RBGW": neopixel.RBGW if ADAFRUIT_AVAILABLE else None,
    "GRBW": neopixel.GRBW if ADAFRUIT_AVAILABLE else None,
    "GBRW": neopixel.GBRW if ADAFRUIT_AVAILABLE else None,
    "BRGW": neopixel.BRGW if ADAFRUIT_AVAILABLE else None,
    "BGRW": neopixel.BGRW if ADAFRUIT_AVAILABLE else None,
}


def map_strip_type_to_pixel_order(strip_type: str) -> str:
    """
    Map rpi_ws281x strip type names to pixel order strings.

    Args:
        strip_type: Strip type name (e.g. "WS2811_STRIP_GRB")

    Returns:
        Pixel order string (e.g. "GRB")
    """
    # Remove common prefixes
    order = strip_type.replace("WS2811_STRIP_", "").replace("SK6812_STRIP_", "")
    # Validate it's a known order
    if order not in PIXEL_ORDERS:
        # Default to GRB if unknown
        return "GRB"
    return order


class AdafruitNeoPixelPWMBackend(LEDBackend):
    """
    LED backend using Adafruit CircuitPython NeoPixel library (PWM-based).

    This backend is designed for maximum compatibility across all Raspberry Pi
    models including Pi 5. It uses the PWM interface with configurable GPIO pin.

    Configuration parameters:
        pin (int): GPIO pin number (required, e.g. 10, 18, 21)
        count (int): Number of LEDs (required)
        brightness (int): Brightness percentage 0-100 (optional, default 100)
        pixel_order (str): Pixel order like "GRB", "RGB", "RGBW" (optional, default "GRB")
        auto_write (bool): Whether to auto-write on pixel changes (optional, default False)

    Note: The following rpi_ws281x parameters are NOT used by this backend:
        - freq_hz: Determined by hardware
        - dma: Not applicable
        - channel: Not applicable
        - invert: Not supported
        - type: Use pixel_order instead (but will be auto-converted if provided)
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the Adafruit NeoPixel PWM backend.

        Args:
            config: Configuration dictionary with LED settings

        Raises:
            ImportError: If Adafruit libraries are not installed
            ValueError: If configuration is invalid
        """
        if not ADAFRUIT_AVAILABLE:
            raise ImportError(
                "Adafruit CircuitPython NeoPixel library not available. "
                "Install with: pip install adafruit-circuitpython-neopixel"
            )

        self.config = config
        self._pixels = None
        self._num_pixels = int(config["count"])

        # GPIO pin - required
        if "pin" not in config:
            raise ValueError("GPIO pin number is required (config['pin'])")
        self._pin = int(config["pin"])

        # Validate pin number (basic range check)
        if self._pin < 0 or self._pin > 27:
            raise ValueError(f"Invalid GPIO pin number: {self._pin} (must be 0-27)")

        # Brightness: convert percentage (0-100) to float (0.0-1.0)
        brightness_percent = int(config.get("brightness", 100))
        self._brightness = max(0.0, min(1.0, brightness_percent / 100.0))

        # Pixel order - try to map from strip type if provided
        pixel_order_str = config.get("pixel_order", None)
        if pixel_order_str is None and "type" in config:
            # Map from strip_type (rpi_ws281x format)
            pixel_order_str = map_strip_type_to_pixel_order(config["type"])
        if pixel_order_str is None:
            pixel_order_str = "GRB"  # Default for most NeoPixels

        # Validate pixel order
        if pixel_order_str not in PIXEL_ORDERS:
            raise ValueError(
                f"Invalid pixel order: {pixel_order_str}. "
                f"Supported: {', '.join(PIXEL_ORDERS.keys())}"
            )

        self._pixel_order = PIXEL_ORDERS[pixel_order_str]
        self._pixel_order_str = pixel_order_str
        self._has_white = pixel_order_str.endswith("W")

        # Auto-write should be False to allow buffering
        self._auto_write = config.get("auto_write", False)

        # Buffer for pixel colors (stored as (r, g, b) or (r, g, b, w) tuples)
        self._buffer = [(0, 0, 0, 0) if self._has_white else (0, 0, 0)] * self._num_pixels

    def begin(self) -> None:
        """
        Initialize the LED hardware.

        Creates the NeoPixel object and prepares it for use.

        Raises:
            RuntimeError: If initialization fails
        """
        try:
            # Get the GPIO pin using board.D{pin} notation
            pin_attr = f"D{self._pin}"
            if not hasattr(board, pin_attr):
                raise ValueError(
                    f"GPIO pin {self._pin} not available on this board. "
                    f"Try common pins: 10, 18, or 21"
                )

            pin = getattr(board, pin_attr)

            # Create NeoPixel object
            self._pixels = NeoPixel(
                pin,
                self._num_pixels,
                brightness=self._brightness,
                auto_write=self._auto_write,
                pixel_order=self._pixel_order,
            )

            # Initialize all pixels to off
            self._pixels.fill((0, 0, 0, 0) if self._has_white else (0, 0, 0))
            if not self._auto_write:
                self._pixels.show()

        except Exception as e:
            raise RuntimeError(f"Failed to initialize NeoPixel on GPIO {self._pin}: {e}") from e

    def show(self) -> None:
        """Update the LED strip with buffered pixel colors."""
        if self._pixels is not None:
            self._pixels.show()

    def set_brightness(self, value: int) -> None:
        """
        Set global brightness.

        Args:
            value: Brightness value 0-255

        Note: This affects future pixel updates by scaling color values.
        """
        # Convert 0-255 to 0.0-1.0
        self._brightness = max(0.0, min(1.0, value / 255.0))
        if self._pixels is not None:
            self._pixels.brightness = self._brightness

    def get_brightness(self) -> int:
        """
        Get current brightness.

        Returns:
            Brightness value 0-255
        """
        return int(self._brightness * 255)

    def num_pixels(self) -> int:
        """
        Get the number of pixels.

        Returns:
            Number of LEDs
        """
        return self._num_pixels

    def set_pixel_color(self, index: int, color: int) -> None:
        """
        Set pixel color using packed 32-bit integer.

        Args:
            index: Pixel index (0-based)
            color: Color as 32-bit integer (0xWWRRGGBB or 0xRRGGBB)
        """
        # Extract RGBW components from packed integer
        w = (color >> 24) & 0xFF
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF

        self.set_pixel_color_rgb(index, r, g, b, w)

    def set_pixel_color_rgb(
        self, index: int, r: int, g: int, b: int, w: int = 0
    ) -> None:
        """
        Set pixel color using separate RGB(W) values.

        Args:
            index: Pixel index (0-based)
            r: Red value 0-255
            g: Green value 0-255
            b: Blue value 0-255
            w: White value 0-255 (for RGBW strips)
        """
        if self._pixels is None:
            return

        if index < 0 or index >= self._num_pixels:
            return

        # Store in buffer
        if self._has_white:
            self._buffer[index] = (r, g, b, w)
            # Set pixel with RGBW
            self._pixels[index] = (r, g, b, w)
        else:
            self._buffer[index] = (r, g, b)
            # Set pixel with RGB only
            self._pixels[index] = (r, g, b)

    def get_pixel_color(self, index: int) -> int:
        """
        Get pixel color as packed 32-bit integer.

        Args:
            index: Pixel index (0-based)

        Returns:
            Color as 32-bit integer (0xWWRRGGBB)
        """
        r, g, b, w = self.get_pixel_color_rgb(index)
        return (w << 24) | (r << 16) | (g << 8) | b

    def get_pixel_color_rgb(self, index: int) -> Tuple[int, int, int, int]:
        """
        Get pixel color as separate RGBW values.

        Args:
            index: Pixel index (0-based)

        Returns:
            Tuple of (r, g, b, w) values
        """
        if index < 0 or index >= self._num_pixels:
            return (0, 0, 0, 0)

        # Get from buffer
        if self._has_white:
            r, g, b, w = self._buffer[index]
            return (r, g, b, w)
        else:
            r, g, b = self._buffer[index]
            return (r, g, b, 0)

    def cleanup(self) -> None:
        """Clean up resources and turn off all LEDs."""
        if self._pixels is not None:
            try:
                self._pixels.fill((0, 0, 0, 0) if self._has_white else (0, 0, 0))
                self._pixels.show()
                self._pixels.deinit()
            except Exception:
                pass  # Ignore cleanup errors
            finally:
                self._pixels = None

    @staticmethod
    def is_available() -> bool:
        """
        Check if the Adafruit NeoPixel PWM backend is available.

        Returns:
            True if backend dependencies are installed
        """
        return ADAFRUIT_AVAILABLE
