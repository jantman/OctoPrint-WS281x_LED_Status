# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Raspberry Pi 5 Support**: The plugin now supports Raspberry Pi 5 through a new LED backend system
  - New LED backend abstraction layer allows multiple hardware control libraries
  - Adafruit CircuitPython NeoPixel SPI backend for Pi 5 compatibility
  - Backend selection in plugin settings UI
  - Comprehensive documentation for Pi 5 setup and backend configuration
  - Support for 12 pixel orders including RGBW variants in Adafruit backend

### Changed

- Settings schema updated to version 4 to support backend selection
- LED control logic refactored to use backend abstraction instead of direct rpi_ws281x calls
- Setup instructions updated to include backend selection step
- Plugin now supports multiple LED control backends:
  - `rpi_ws281x`: Original backend for Raspberry Pi 3/4 (default)
  - `adafruit`: Adafruit CircuitPython NeoPixel SPI backend for Raspberry Pi 5
- **Dependencies updated**: Both `rpi_ws281x` and `adafruit-circuitpython-neopixel-spi` are now installed automatically by OctoPrint's Plugin Manager
  - No manual pip installation required
  - All dependencies installed for all users, backend selection determines which is used

### Migration Notes

**For existing users:**
- Your settings will be automatically migrated from version 3 to version 4
- The plugin will continue using the `rpi_ws281x` backend by default
- No action is required unless you want to switch to Raspberry Pi 5 or try a different backend
- All your existing configurations (pin settings, strip types, effects) are preserved

**For Raspberry Pi 5 users:**
- After upgrading, go to plugin settings and select the "Adafruit CircuitPython NeoPixel SPI" backend
- Dependencies are installed automatically by OctoPrint's Plugin Manager
- You only need to enable SPI in raspi-config and add your user to the `spi` group
- Note that the Adafruit backend uses GPIO 10 (physical pin 19) for data output via SPI
- See `docs/features/adafruit_backend_requirements.md` for detailed setup instructions

### Technical Details

This release includes a major refactoring to support multiple LED control backends:

**Milestone 1: LED Backend Abstraction Layer** (7 commits)
- Created abstract `LEDBackend` interface
- Implemented `RpiWS281xBackend` wrapper for existing functionality
- Added backend factory and registry system
- Updated `StripSegment` and `EffectRunner` to use backend abstraction
- Added 70 new unit tests for backend system

**Milestone 2: Backend Selection Configuration** (1 commit)
- Extended settings schema to version 4 with backend selection
- Implemented automatic settings migration from version 3
- Added backend selection UI in plugin settings
- Added 7 new tests for settings migration

**Milestone 3: Adafruit Backend Implementation** (6 commits)
- Implemented full Adafruit CircuitPython NeoPixel SPI backend
- Added backend availability detection (checks for libraries and SPI)
- Updated UI to show backend options with availability status
- Created comprehensive setup documentation
- Added 25 new unit tests for Adafruit backend
- Total test count: 109 tests (84 existing + 25 new)

**Total changes:**
- 14 commits implementing Pi 5 support
- 109 unit tests passing (32 new tests added)
- Full backward compatibility maintained
- Zero breaking changes for existing users

---

## [0.8.1] - (Previous Release)

See [GitHub Releases](https://github.com/cp2004/OctoPrint-WS281x_LED_Status/releases) for detailed information about previous versions.

## [0.8.0] - (Previous Release)

See [GitHub Releases](https://github.com/cp2004/OctoPrint-WS281x_LED_Status/releases) for detailed information about previous versions.

---

For a complete history of changes, see the [GitHub Releases page](https://github.com/cp2004/OctoPrint-WS281x_LED_Status/releases) or the git commit history.
