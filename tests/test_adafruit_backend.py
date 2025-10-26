__author__ = "Jason Antman <jason@jasonantman.com>"
__license__ = "GNU Affero General Public License http://www.gnu.org/licenses/agpl.html"
__copyright__ = "Copyright (c) Jason Antman 2025 - released under the terms of the AGPLv3 License"

import unittest
from typing import Any, Dict
from unittest import mock
import sys

# Mock the Adafruit libraries before importing the backend
sys.modules["board"] = mock.MagicMock()
sys.modules["neopixel_spi"] = mock.MagicMock()

from octoprint_ws281x_led_status.backend.adafruit_neopixel_spi_backend import (
    AdafruitNeoPixelSPIBackend,
    map_strip_type_to_pixel_order,
    PIXEL_ORDERS,
)


class TestPixelOrderMapping(unittest.TestCase):
    """Test pixel order mapping from strip types."""

    def test_map_ws2811_strip_types(self):
        """Test mapping WS2811 strip types to pixel orders."""
        self.assertEqual(map_strip_type_to_pixel_order("WS2811_STRIP_GRB"), "GRB")
        self.assertEqual(map_strip_type_to_pixel_order("WS2811_STRIP_RGB"), "RGB")
        self.assertEqual(map_strip_type_to_pixel_order("WS2811_STRIP_RBG"), "RBG")

    def test_map_sk6812_strip_types(self):
        """Test mapping SK6812 strip types to pixel orders."""
        self.assertEqual(map_strip_type_to_pixel_order("SK6812_STRIP_RGBW"), "RGBW")
        self.assertEqual(map_strip_type_to_pixel_order("SK6812_STRIP_GRBW"), "GRBW")

    def test_map_unknown_defaults_to_grb(self):
        """Test that unknown strip types default to GRB."""
        self.assertEqual(map_strip_type_to_pixel_order("UNKNOWN_TYPE"), "GRB")
        self.assertEqual(map_strip_type_to_pixel_order(""), "GRB")


class TestAdafruitBackendInit(unittest.TestCase):
    """Test Adafruit backend initialization."""

    def test_init_with_minimal_config(self):
        """Test initialization with minimal configuration."""
        config = {"count": 24}
        backend = AdafruitNeoPixelSPIBackend(config)

        self.assertEqual(backend.num_pixels(), 24)
        self.assertEqual(backend.get_brightness(), 255)  # Default 100%
        self.assertEqual(backend._pixel_order_str, "GRB")  # Default

    def test_init_with_full_config(self):
        """Test initialization with full configuration."""
        config = {
            "count": 50,
            "brightness": 75,
            "pixel_order": "RGB",
        }
        backend = AdafruitNeoPixelSPIBackend(config)

        self.assertEqual(backend.num_pixels(), 50)
        self.assertEqual(backend.get_brightness(), 191)  # 75% of 255
        self.assertEqual(backend._pixel_order_str, "RGB")

    def test_init_maps_strip_type_to_pixel_order(self):
        """Test that strip type is mapped to pixel order if pixel_order not provided."""
        config = {"count": 24, "type": "WS2811_STRIP_GRB"}
        backend = AdafruitNeoPixelSPIBackend(config)

        self.assertEqual(backend._pixel_order_str, "GRB")

    def test_init_with_rgbw(self):
        """Test initialization with RGBW pixel order."""
        config = {"count": 24, "pixel_order": "GRBW"}
        backend = AdafruitNeoPixelSPIBackend(config)

        self.assertTrue(backend._has_white)
        self.assertEqual(len(backend._pixel_order), 4)

    def test_init_with_invalid_pixel_order_raises(self):
        """Test that invalid pixel order raises ValueError."""
        config = {"count": 24, "pixel_order": "INVALID"}

        with self.assertRaises(ValueError) as cm:
            AdafruitNeoPixelSPIBackend(config)

        self.assertIn("Invalid pixel order", str(cm.exception))

    def test_brightness_percentage_conversion(self):
        """Test brightness conversion from percentage to float."""
        # 0%
        backend = AdafruitNeoPixelSPIBackend({"count": 24, "brightness": 0})
        self.assertEqual(backend.get_brightness(), 0)

        # 50%
        backend = AdafruitNeoPixelSPIBackend({"count": 24, "brightness": 50})
        self.assertEqual(backend.get_brightness(), 127)  # 50% of 255

        # 100%
        backend = AdafruitNeoPixelSPIBackend({"count": 24, "brightness": 100})
        self.assertEqual(backend.get_brightness(), 255)


class TestAdafruitBackendMethods(unittest.TestCase):
    """Test Adafruit backend methods with mocked NeoPixel_SPI."""

    def setUp(self):
        """Create mock backend for each test."""
        self.config = {"count": 10, "brightness": 100, "pixel_order": "GRB"}
        self.backend = AdafruitNeoPixelSPIBackend(self.config)

        # Mock the pixels object
        self.mock_pixels = mock.MagicMock()
        self.backend._pixels = self.mock_pixels

    def test_set_pixel_color_rgb(self):
        """Test setting pixel color with RGB values."""
        self.backend.set_pixel_color_rgb(5, 255, 128, 64, 0)

        # Should set the pixel on the mock object
        self.mock_pixels.__setitem__.assert_called_once_with(5, (255, 128, 64))

    def test_set_pixel_color_rgbw(self):
        """Test setting pixel color with RGBW values."""
        # Create RGBW backend
        config = {"count": 10, "pixel_order": "RGBW"}
        backend = AdafruitNeoPixelSPIBackend(config)
        backend._pixels = mock.MagicMock()

        backend.set_pixel_color_rgb(3, 255, 128, 64, 32)

        # Should set all four components
        backend._pixels.__setitem__.assert_called_once_with(3, (255, 128, 64, 32))

    def test_set_pixel_color_packed(self):
        """Test setting pixel color with packed integer."""
        # Color: 0x00FF8040 = R:255, G:128, B:64
        self.backend.set_pixel_color(5, 0x00FF8040)

        self.mock_pixels.__setitem__.assert_called_once_with(5, (255, 128, 64))

    def test_get_pixel_color_rgb(self):
        """Test getting pixel color as RGB tuple."""
        # Set a color in the buffer
        self.backend._buffer[5] = (255, 128, 64)

        r, g, b, w = self.backend.get_pixel_color_rgb(5)

        self.assertEqual((r, g, b, w), (255, 128, 64, 0))

    def test_get_pixel_color_packed(self):
        """Test getting pixel color as packed integer."""
        # Set a color in the buffer
        self.backend._buffer[5] = (255, 128, 64)

        color = self.backend.get_pixel_color(5)

        # 0x00FF8040
        self.assertEqual(color, 0x00FF8040)

    def test_get_pixel_color_out_of_bounds(self):
        """Test getting pixel color for out of bounds index."""
        r, g, b, w = self.backend.get_pixel_color_rgb(999)

        self.assertEqual((r, g, b, w), (0, 0, 0, 0))

    def test_set_brightness(self):
        """Test setting brightness."""
        self.backend.set_brightness(128)  # 50% of 255

        self.assertEqual(self.backend.get_brightness(), 128)
        self.mock_pixels.brightness = 0.5019607843137255  # 128/255

    def test_get_brightness(self):
        """Test getting brightness."""
        self.backend._brightness = 0.5

        brightness = self.backend.get_brightness()

        self.assertEqual(brightness, 127)  # 50% of 255

    def test_show(self):
        """Test show method calls pixels.show()."""
        self.backend.show()

        self.mock_pixels.show.assert_called_once()

    def test_cleanup(self):
        """Test cleanup turns off LEDs and deinits."""
        self.backend.cleanup()

        self.mock_pixels.fill.assert_called_once_with(0)
        self.mock_pixels.show.assert_called_once()
        self.mock_pixels.deinit.assert_called_once()


class TestAdafruitBackendBegin(unittest.TestCase):
    """Test Adafruit backend begin() method."""

    @mock.patch("octoprint_ws281x_led_status.backend.adafruit_neopixel_spi_backend.board")
    @mock.patch("octoprint_ws281x_led_status.backend.adafruit_neopixel_spi_backend.neopixel_spi")
    def test_begin_creates_pixels(self, mock_neopixel_spi, mock_board):
        """Test begin() creates NeoPixel_SPI object."""
        mock_spi = mock.MagicMock()
        mock_board.SPI.return_value = mock_spi
        mock_pixels = mock.MagicMock()
        mock_neopixel_spi.NeoPixel_SPI.return_value = mock_pixels

        config = {"count": 24, "brightness": 75, "pixel_order": "GRB"}
        backend = AdafruitNeoPixelSPIBackend(config)
        backend.begin()

        # Verify NeoPixel_SPI was created with correct parameters
        mock_neopixel_spi.NeoPixel_SPI.assert_called_once()
        call_args = mock_neopixel_spi.NeoPixel_SPI.call_args

        self.assertEqual(call_args[0][0], mock_spi)  # SPI object
        self.assertEqual(call_args[0][1], 24)  # num_pixels
        self.assertEqual(call_args[1]["bpp"], 3)  # bytes per pixel (RGB)
        self.assertAlmostEqual(call_args[1]["brightness"], 0.75, places=2)

        # Verify pixels were initialized to off
        mock_pixels.fill.assert_called_once_with(0)
        mock_pixels.show.assert_called_once()

    @mock.patch("octoprint_ws281x_led_status.backend.adafruit_neopixel_spi_backend.board")
    @mock.patch("octoprint_ws281x_led_status.backend.adafruit_neopixel_spi_backend.neopixel_spi")
    def test_begin_with_rgbw(self, mock_neopixel_spi, mock_board):
        """Test begin() with RGBW pixel order."""
        mock_spi = mock.MagicMock()
        mock_board.SPI.return_value = mock_spi
        mock_pixels = mock.MagicMock()
        mock_neopixel_spi.NeoPixel_SPI.return_value = mock_pixels

        config = {"count": 24, "pixel_order": "GRBW"}
        backend = AdafruitNeoPixelSPIBackend(config)
        backend.begin()

        call_args = mock_neopixel_spi.NeoPixel_SPI.call_args
        self.assertEqual(call_args[1]["bpp"], 4)  # bytes per pixel (RGBW)


class TestIsAvailable(unittest.TestCase):
    """Test backend availability detection."""

    @mock.patch("os.access")
    @mock.patch("os.path.exists")
    @mock.patch("octoprint_ws281x_led_status.backend.adafruit_neopixel_spi_backend.ADAFRUIT_AVAILABLE", True)
    def test_is_available_all_conditions_met(self, mock_exists, mock_access):
        """Test is_available returns True when all conditions met."""
        mock_exists.return_value = True
        mock_access.return_value = True

        from octoprint_ws281x_led_status.backend.adafruit_neopixel_spi_backend import (
            is_available,
        )

        self.assertTrue(is_available())

    @mock.patch("octoprint_ws281x_led_status.backend.adafruit_neopixel_spi_backend.ADAFRUIT_AVAILABLE", False)
    def test_is_available_libraries_not_installed(self):
        """Test is_available returns False when libraries not installed."""
        from octoprint_ws281x_led_status.backend.adafruit_neopixel_spi_backend import (
            is_available,
        )

        self.assertFalse(is_available())

    @mock.patch("os.path.exists")
    @mock.patch("octoprint_ws281x_led_status.backend.adafruit_neopixel_spi_backend.ADAFRUIT_AVAILABLE", True)
    def test_is_available_spi_device_missing(self, mock_exists):
        """Test is_available returns False when SPI device doesn't exist."""
        mock_exists.return_value = False

        from octoprint_ws281x_led_status.backend.adafruit_neopixel_spi_backend import (
            is_available,
        )

        self.assertFalse(is_available())

    @mock.patch("os.access")
    @mock.patch("os.path.exists")
    @mock.patch("octoprint_ws281x_led_status.backend.adafruit_neopixel_spi_backend.ADAFRUIT_AVAILABLE", True)
    def test_is_available_spi_not_writable(self, mock_exists, mock_access):
        """Test is_available returns False when SPI device not writable."""
        mock_exists.return_value = True
        mock_access.return_value = False

        from octoprint_ws281x_led_status.backend.adafruit_neopixel_spi_backend import (
            is_available,
        )

        self.assertFalse(is_available())


if __name__ == "__main__":
    unittest.main()
