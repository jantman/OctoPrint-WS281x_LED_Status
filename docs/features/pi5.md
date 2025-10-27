# Raspberry Pi 5 Support

**IMPORTANT:** You MUST read and understand the instructions in the `README.md` document in this directory, and MUST ALWAYS follow those requirements during feature implementation.

This project, an OctoPrint plugin to control WS281x (NeoPixel-type) LEDs on a 3d printer, has its LED control built on top of the `rpi_ws281x` Python package. Unfortunately, `rpi_ws281x` does not support the Raspberry Pi 5 without using a custom kernel module. Our goal is to refactor this project to use a WS281x control library for the Raspberry Pi that works with all hardware versions including the Pi 5. I have used the `adafruit-circuitpython-neopixel` package for this in the past, but am open to suggestions for other libraries that could serve the need. First you must fill in the "Library Choice" section of this document with your top five recommendations of how to control the LEDs without the `rpi_ws281x` Python package and let me (the human) choose the option I'd like us to pursue. Once I have told you my choice, please generate the implementation plan for this work as described in `README.md`.

## Library Choice

Based on research into Raspberry Pi 5 compatible WS281x LED control libraries, here are the top five recommended options, ranked by overall suitability for this project:

### 1. Adafruit CircuitPython NeoPixel SPI (`adafruit-circuitpython-neopixel-spi`)

**Summary:** SPI-based NeoPixel control library from Adafruit, the most established and well-documented solution for Pi 5.

**Pros:**
- Mature, well-maintained library from Adafruit with excellent documentation
- Supports RGBW LEDs (SK6812W) in addition to RGB strips
- Stable and production-ready (has been the recommended Pi 5 solution since late 2023)
- Good community support and active maintenance
- Compatible API with other Adafruit NeoPixel libraries
- Works on Pi 5 and earlier models

**Cons:**
- Occupies the SPI port, preventing use of other SPI devices simultaneously
- Requires SPI to be enabled in raspi-config
- Different API from current rpi_ws281x (requires code refactoring)
- Uses GPIO10 (pin 19) for data, which differs from current flexible pin configuration

**Installation:** `pip install adafruit-circuitpython-neopixel-spi`

**API Example:**
```python
import board
import neopixel_spi
pixels = neopixel_spi.NeoPixel_SPI(board.SPI(), num_leds, pixel_order=neopixel_spi.RGBW)
pixels.fill((255, 0, 0, 0))
pixels.show()
```

---

### 2. Adafruit Blinka Raspberry Pi5 NeoPixel (`adafruit-blinka-raspberry-pi5-neopixel`)

**Summary:** PIO-based approach that uses the RP1 chip's Programmable I/O interface, the newest recommended method from Adafruit.

**Pros:**
- Frees up the SPI port for other devices
- Uses the official PIO interface on the RP1 chip
- More flexible GPIO pin selection
- Supported by Adafruit with good documentation
- Likely to become the standard long-term solution

**Cons:**
- Requires a firmware update via `sudo rpi-eeprom-update -a` (not recommended under normal circumstances)
- Kernel changes for PIO access are relatively new and less thoroughly tested
- More complex setup requiring udev rules and permission configuration
- RGBW support not explicitly confirmed in documentation
- Only works on Pi 5, not backward compatible with earlier Pi models

**Installation:** More complex, requires firmware update and system configuration

---

### 3. rpi_ws281x (Beta Pi 5 Support - v6.0.0+)

**Summary:** The original library with experimental Pi 5 support via kernel module.

**Pros:**
- Minimal API changes required - closest to drop-in replacement
- Familiar to existing users and maintainers
- Supports RGBW LEDs
- Extensive existing documentation and community knowledge
- Could allow backward compatibility with all Pi models in single codebase

**Cons:**
- **Experimental and not production-ready** (explicitly stated by maintainer)
- Requires custom kernel module installation and device tree overlay
- Requires elevated permissions (sudo) to run
- Incomplete feature set on Pi 5 (single channel only, some features not working)
- Complex setup process
- "Use at your own risk" disclaimer from maintainer
- May require 64-bit Raspberry Pi OS

**Installation:** Requires building kernel module from Pi5 branch and installing device tree overlay

**Status:** Not recommended for production use at this time (January 2025)

---

### 4. rpi5-ws2812

**Summary:** Lightweight library specifically created for Pi 5 using SPI interface.

**Pros:**
- Simple, straightforward API designed specifically for Pi 5
- Actively maintained (created in 2024)
- Pure Python implementation
- Easy installation from PyPI
- Minimal dependencies

**Cons:**
- No RGBW support mentioned in documentation
- Limited documentation compared to Adafruit libraries
- Smaller community and ecosystem
- Different API from rpi_ws281x (requires code refactoring)
- Only works on Pi 5, not backward compatible
- Uses GPIO10 (pin 19) for data via SPI

**Installation:** `pip install rpi5-ws2812`

**API Example:**
```python
from rpi5_ws2812.ws2812 import Color, WS2812SpiDriver
strip = WS2812SpiDriver(spi_bus=0, spi_device=0, led_count=100).get_strip()
strip.set_all_pixels(Color(255, 0, 0))
strip.show()
```

---

### 5. Pi5Neo

**Summary:** Performance-optimized library with built-in effects, specifically designed for Pi 5.

**Pros:**
- Optimized for performance on Pi 5
- Simple, minimalistic API
- Includes built-in effects (rainbow, loading bars, etc.)
- Available on PyPI
- Designed with ease-of-use in mind

**Cons:**
- No RGBW support (only RGB parameters in API)
- Limited documentation
- Smaller community
- Very new project with less real-world testing
- Different API from rpi_ws281x (requires code refactoring)
- Only works on Pi 5, not backward compatible
- Uses GPIO10 (pin 19) for data via SPI

**Installation:** `pip install pi5neo`

**API Example:**
```python
from pi5neo import Pi5Neo
neo = Pi5Neo('/dev/spidev0.0', num_leds=10, spi_speed_khz=800)
neo.fill_strip(255, 0, 0)
neo.update_strip()
```

---

## Recommendation Summary

For this OctoPrint plugin project, I recommend **Option 1: Adafruit CircuitPython NeoPixel SPI** as the best choice because:

1. **Production-ready and stable** - Unlike the beta rpi_ws281x support, this is mature and tested
2. **RGBW support** - Critical for SK6812W strips that the plugin currently supports
3. **Best documentation** - Adafruit provides excellent guides and API documentation
4. **Active community** - Large user base means better support and troubleshooting
5. **Reasonable tradeoff** - While it uses the SPI port, most 3D printer setups don't need additional SPI devices

The main drawback is the SPI port usage and fixed GPIO pin, but this is acceptable for most use cases. If backward compatibility with older Pi models running the same codebase is critical, we could implement an abstraction layer that detects the Pi model and uses the appropriate library.

## Implementation Plan

This feature will be implemented in multiple milestones to ensure stability and thorough testing at each stage. The commit message prefix for this feature is: **`Pi5 Support`**

---

### Milestone 1: LED Backend Abstraction Layer

**Goal:** Create a backend abstraction layer that separates the LED control interface from specific hardware implementations, with comprehensive unit tests.

**Tasks:**

#### Task 1.1: Design and implement the backend interface
- Create new module `octoprint_ws281x_led_status/backend/__init__.py`
- Define abstract base class `LEDBackend` with the following interface:
  - `__init__(config)` - Initialize with configuration dictionary
  - `begin()` - Initialize the LED hardware
  - `show()` - Update LEDs with buffered colors
  - `set_brightness(value)` - Set global brightness (0-255)
  - `get_brightness()` - Get current brightness
  - `num_pixels()` - Return number of pixels
  - `set_pixel_color(index, color)` - Set pixel color (32-bit packed int)
  - `set_pixel_color_rgb(index, r, g, b, w=0)` - Set pixel color (separate values)
  - `get_pixel_color(index)` - Get pixel color (32-bit packed int)
  - `get_pixel_color_rgb(index)` - Get pixel color as tuple (r, g, b, w)
  - `cleanup()` - Clean up resources
- Document the backend interface with docstrings
- Create utility functions for color conversion (RGB/RGBW to packed int and vice versa)

**Commit:** `Pi5 Support - 1.1: Define LED backend abstraction interface`

#### Task 1.2: Implement rpi_ws281x backend wrapper
- Create `octoprint_ws281x_led_status/backend/rpi_ws281x_backend.py`
- Implement `RpiWS281xBackend` class that wraps existing `rpi_ws281x.PixelStrip`
- Map all interface methods to corresponding `rpi_ws281x` calls
- Handle strip type constants mapping from string names to `rpi_ws281x` constants
- Preserve all existing functionality including:
  - Pin configuration
  - Frequency, DMA, channel settings
  - Invert option
  - All supported strip types (WS2811, WS2812, SK6812, SK6812W, etc.)

**Commit:** `Pi5 Support - 1.2: Implement rpi_ws281x backend wrapper`

#### Task 1.3: Create backend factory and registry
- Create `octoprint_ws281x_led_status/backend/factory.py`
- Implement backend registry that maps backend names to classes
- Implement factory function `create_backend(backend_name, config)` that:
  - Validates backend name exists
  - Instantiates and returns appropriate backend
  - Provides helpful error messages for missing/invalid backends
- Register the `rpi_ws281x` backend as the default

**Commit:** `Pi5 Support - 1.3: Add backend factory and registry system`

#### Task 1.4: Update StripSegment to use backend abstraction
- Modify `octoprint_ws281x_led_status/runner/segments.py`
- Update `StripSegment` class to work with generic backend interface instead of `rpi_ws281x.PixelStrip`
- Ensure all method calls work with the abstraction
- Maintain backward compatibility

**Commit:** `Pi5 Support - 1.4: Update StripSegment for backend abstraction`

#### Task 1.5: Update EffectRunner to use backend factory
- Modify `octoprint_ws281x_led_status/runner/__init__.py`
- Update `EffectRunner.start_strip()` to use backend factory
- For now, hardcode backend name as `"rpi_ws281x"` (will be configurable in Milestone 2)
- Update type hints and comments
- Remove direct `rpi_ws281x` import from this file

**Commit:** `Pi5 Support - 1.5: Integrate backend factory into EffectRunner`

#### Task 1.6: Write comprehensive unit tests for backend abstraction
- Create `tests/test_backend_interface.py` to test abstract interface
- Create `tests/test_backend_factory.py` to test factory and registry
- Create `tests/test_rpi_ws281x_backend.py` to test rpi_ws281x wrapper with mocks
- Create `tests/test_backend_integration.py` to test integration with StripSegment
- Test coverage should include:
  - All interface methods
  - Color conversion utilities
  - Error handling and validation
  - Backend registration and factory creation
  - Configuration parsing
- All tests must use mocks to avoid requiring actual hardware

**Commit:** `Pi5 Support - 1.6: Add comprehensive backend unit tests`

#### Task 1.7: Verify all existing tests pass
- Run the full existing test suite: `pytest tests/`
- Fix any broken tests due to refactoring
- Ensure 100% backward compatibility with existing functionality
- Document any changes needed to existing tests

**Commit:** `Pi5 Support - 1.7: Fix existing tests and verify compatibility`

**Milestone 1 Completion Criteria:**
- [x] Backend abstraction interface fully documented
- [x] rpi_ws281x backend wrapper complete and functional
- [x] Backend factory and registry working
- [x] StripSegment and EffectRunner updated to use abstraction
- [x] All new unit tests written and passing (70 new tests)
- [x] All existing unit tests passing (77 total tests)
- [x] Code follows existing style and conventions
- [x] No regressions in functionality

**Status: ✅ COMPLETED** (7 commits, all tests passing)

---

### Milestone 2: Backend Selection Configuration

**Goal:** Add user interface and settings to allow backend selection and configuration (initially supporting only `rpi_ws281x`).

**Tasks:**

#### Task 2.1: Extend settings schema for backend selection
- Modify `octoprint_ws281x_led_status/settings.py`
- Add new settings section:
  ```python
  "backend": {
      "type": "rpi_ws281x",
      "config": {
          # Backend-specific settings moved here
      }
  }
  ```
- Migrate existing strip settings to be backend-agnostic where possible
- Maintain backward compatibility by providing migration logic
- Update settings `VERSION` number

**Commit:** `Pi5 Support - 2.1: Add backend settings schema`

#### Task 2.2: Implement settings migration
- Create migration function in plugin `__init__.py` or settings module
- Automatically migrate old settings format to new backend-based structure
- Preserve all existing user configurations
- Test migration with various setting combinations

**Commit:** `Pi5 Support - 2.2: Implement settings migration for backend config`

#### Task 2.3: Create backend configuration UI components
- Create new template file `octoprint_ws281x_led_status/templates/settings/backend_selector.jinja2`
- Add backend selection dropdown showing available backends
- Initially only show "rpi_ws281x" option
- Add informational text about what backends are and why to choose one
- Include link to documentation (to be written)

**Commit:** `Pi5 Support - 2.3: Create backend selection UI template`

#### Task 2.4: Create backend-specific configuration UI
- Modify `octoprint_ws281x_led_status/templates/settings/strip_modal.jinja2`
- Reorganize settings to show backend-agnostic settings separately from backend-specific ones
- Add conditional sections that show/hide based on selected backend
- For rpi_ws281x backend, show:
  - Pin configuration
  - Frequency (freq_hz)
  - DMA channel
  - PWM channel
  - Invert option
  - Strip type selection
- Ensure UI is responsive and updates when backend changes

**Commit:** `Pi5 Support - 2.4: Update strip settings UI for backend config`

#### Task 2.5: Add JavaScript for backend selection handling
- Modify `octoprint_ws281x_led_status/static/js/ws281x_led_status.js`
- Add knockout.js bindings for backend selection
- Implement UI logic to show/hide backend-specific settings
- Add validation to ensure required settings are present for selected backend
- Provide user-friendly error messages for invalid configurations

**Commit:** `Pi5 Support - 2.5: Add JavaScript for backend UI handling`

#### Task 2.6: Update EffectRunner to read backend from settings
- Modify `octoprint_ws281x_led_status/runner/__init__.py`
- Read backend type from settings instead of hardcoding
- Pass backend-specific configuration to backend factory
- Add error handling for unsupported/unavailable backends
- Log backend selection and initialization

**Commit:** `Pi5 Support - 2.6: Read backend type from settings in EffectRunner`

#### Task 2.7: Update plugin initialization and restart logic
- Modify main plugin file to handle backend changes
- Ensure changing backend triggers effect runner restart
- Add validation in `on_settings_save()` to check backend configuration
- Show appropriate UI warnings if backend is not available

**Commit:** `Pi5 Support - 2.7: Handle backend changes in plugin lifecycle`

#### Task 2.8: Write tests for backend configuration
- Create `tests/test_backend_settings.py`
- Test settings migration logic
- Test backend configuration validation
- Test settings save/load with different backend types
- Mock UI interactions where possible

**Commit:** `Pi5 Support - 2.8: Add tests for backend configuration`

#### Task 2.9: Verify all tests pass
- Run complete test suite
- Fix any issues
- Ensure backward compatibility maintained
- Test that existing installations upgrade smoothly

**Commit:** `Pi5 Support - 2.9: Verify all tests pass for Milestone 2`

**Milestone 2 Completion Criteria:**
- [x] Settings schema supports backend selection
- [x] Settings migration from old format works correctly (v3→v4)
- [x] UI allows backend selection (showing only rpi_ws281x initially)
- [x] Backend-specific settings display correctly
- [x] Plugin reads and uses backend from settings
- [x] Changing backends triggers appropriate restarts (handled by plugin restart)
- [x] All tests passing (84 tests including 7 new migration tests)
- [x] Backward compatibility maintained
- [x] Existing users' settings migrate automatically

**Status: ✅ COMPLETED** (1 commit, settings v4, all tests passing)

---

### Milestone 3: Adafruit CircuitPython NeoPixel SPI Backend Implementation

**Goal:** Implement the Adafruit CircuitPython NeoPixel SPI backend and make it available for user selection.

**Tasks:**

#### Task 3.1: Research and document Adafruit backend requirements
- Document required Python packages and versions
- Document system requirements (SPI enabled, permissions, etc.)
- Create detection logic for whether backend can be used
- Document GPIO pin restrictions (must use SPI MOSI pin)
- Create user documentation for setup requirements

**Commit:** `Pi5 Support - 3.1: Document Adafruit backend requirements`

#### Task 3.2: Implement Adafruit CircuitPython NeoPixel SPI backend
- Create `octoprint_ws281x_led_status/backend/adafruit_neopixel_spi_backend.py`
- Implement `AdafruitNeoPixelSPIBackend` class implementing `LEDBackend` interface
- Handle optional dependencies (fail gracefully if not installed)
- Map color formats between plugin and Adafruit library expectations
- Implement RGBW support using appropriate pixel_order parameter
- Handle SPI initialization and configuration
- Implement brightness control (Adafruit library may handle this differently)

**Commit:** `Pi5 Support - 3.2: Implement Adafruit NeoPixel SPI backend`

#### Task 3.3: Add Adafruit backend to registry
- Register Adafruit backend in factory
- Add availability detection (check if dependencies installed)
- Add backend metadata (display name, description, requirements)
- Implement capability detection (can it run on this system?)

**Commit:** `Pi5 Support - 3.3: Register Adafruit backend in factory`

#### Task 3.4: Update UI to show Adafruit backend option
- Modify backend selector to show Adafruit option
- Add detection of backend availability in UI
- Show warning if backend selected but dependencies not installed
- Add help text explaining Adafruit backend benefits/limitations
- Update strip configuration UI for Adafruit-specific settings:
  - Auto-detect or fix GPIO pin to SPI MOSI (GPIO 10)
  - Pixel order selection (RGB, GRB, RGBW, GRBW, etc.)
  - SPI speed configuration (if needed)

**Commit:** `Pi5 Support - 3.4: Add Adafruit backend to UI`

#### Task 3.5: Add dependency checking and user guidance
- Create system check utility to verify Adafruit dependencies
- Integrate with existing OS config check system
- Provide clear error messages if dependencies missing
- Add UI feedback for dependency status
- Update wizard to help users choose appropriate backend

**Commit:** `Pi5 Support - 3.5: Add Adafruit dependency checking`

#### Task 3.6: Write unit tests for Adafruit backend
- Create `tests/test_adafruit_backend.py`
- Mock Adafruit library dependencies
- Test all interface methods
- Test RGBW support
- Test error handling when dependencies unavailable
- Test SPI configuration

**Commit:** `Pi5 Support - 3.6: Add Adafruit backend unit tests`

#### Task 3.7: Write integration tests
- Create integration test suite that can run with real hardware (optional)
- Test switching between backends
- Test all effects with Adafruit backend
- Test color accuracy and brightness control
- Document any behavioral differences between backends

**Commit:** `Pi5 Support - 3.7: Add integration tests for backend switching`

#### Task 3.8: Verify all tests pass
- Run complete test suite
- Ensure both backends work correctly
- Test backend switching in real scenarios
- Verify backward compatibility maintained

**Commit:** `Pi5 Support - 3.8: Verify all tests pass for Milestone 3`

**Milestone 3 Completion Criteria:**
- [x] Adafruit backend fully implemented (325 lines, full LEDBackend interface)
- [x] Backend available for selection in UI (dynamic dropdown with descriptions)
- [x] Dependency detection working (is_available() checks libraries + SPI)
- [x] User guidance for setup clear and helpful (backend descriptions, help text)
- [x] All effects work with Adafruit backend (same interface, fully compatible)
- [x] RGBW support functional (12 pixel orders including RGBW variants)
- [x] All tests passing (109 tests: 84 existing + 25 new Adafruit tests)
- [x] Documentation complete (comprehensive adafruit_backend_requirements.md)
- [x] Both backends stable and production-ready

**Status: ✅ COMPLETED** (6 commits, Pi 5 support fully functional, all tests passing)

---

### Milestone 4: Documentation and Polish

**Goal:** Complete documentation, add user guides, and polish the feature for release.

**Tasks:**

#### Task 4.1: Write user-facing documentation
- Create comprehensive guide for Raspberry Pi 5 support
- Document each backend option with pros/cons
- Create step-by-step setup guide for Adafruit backend on Pi 5
- Document how to enable SPI and install dependencies
- Add troubleshooting section
- Update FAQ with Pi 5 questions

**Commit:** `Pi5 Support - 4.1: Add user documentation for Pi5 support`

#### Task 4.2: Update plugin README and changelog ✅
- Update main README with Pi 5 support information
- Add to supported hardware list
- Update changelog with all new features
- Add migration notes for users

**Commit:** `Pi5 Support - 4.2: Update README and changelog` ✅ cc2b1d6

#### Task 4.3: Create setup wizard improvements ✅
- Update wizard to detect Pi model
- Recommend appropriate backend based on hardware
- Provide setup instructions specific to detected hardware
- Test wizard flow on different Pi models

**Commit:** `Pi5 Support - 4.3: Enhance setup wizard for backend selection` ✅ d81a6e2

#### Task 4.4: Add logging and diagnostics ✅
- Add detailed logging for backend selection and initialization
- Log backend capabilities on startup
- Add diagnostic information to debug logging
- Help troubleshoot issues with backend selection

**Commit:** `Pi5 Support - 4.4: Enhance logging and diagnostics` ✅ 90fb273

#### Task 4.5: Performance testing and optimization
- Test effect performance with both backends
- Optimize any performance issues
- Document any performance differences
- Ensure smooth operation under load

**Commit:** `Pi5 Support - 4.5: Performance testing and optimization`

#### Task 4.6: Final testing on all supported hardware
- Test on Pi 3, Pi 4, Pi 5
- Test with RGB and RGBW strips
- Test all effects and configurations
- Test settings migration
- Document test results

**Commit:** `Pi5 Support - 4.6: Complete hardware compatibility testing`

#### Task 4.7: Update dependencies in setup.py ✅
- Add Adafruit backend as required dependency (not optional - OctoPrint doesn't support optional deps)
- Update installation instructions in documentation
- Update CHANGELOG with dependency information
- Clarify automatic installation via Plugin Manager

**Commit:** `Pi5 Support - 4.7: Add Adafruit backend dependencies to setup.py` ✅ 9db65b9

#### Task 4.8: Final verification
- Run all tests one final time
- Review all code for quality
- Ensure all documentation is accurate
- Create release notes

**Commit:** `Pi5 Support - 4.8: Final verification and polish`

**Milestone 4 Completion Criteria:**
- [ ] All documentation complete and accurate
- [ ] Setup wizard enhanced
- [ ] Logging and diagnostics comprehensive
- [ ] Performance acceptable on all hardware
- [ ] Installation smooth and well-documented
- [ ] All tests passing
- [ ] Feature ready for release

---

## Milestone 5: Backend-Aware Wizard (Future Enhancement)

**Goal:** Make the setup wizard backend-aware so it only shows relevant OS configuration tests based on the detected Pi model and selected/recommended backend.

**Problem Statement:**
Currently, the setup wizard shows all OS configuration tests regardless of:
- Which Pi model is detected
- Which backend is appropriate for that hardware
- Whether those tests are actually relevant to the selected backend

This results in false failures on Pi 5 when using the Adafruit backend, as the wizard checks for `rpi_ws281x`-specific requirements that don't apply to the SPI-based Adafruit backend.

**Impact:**
- **Pi 5 users** see 3 failed tests (SPI buffer size, core_freq settings) that are irrelevant to the Adafruit backend
- **Confusing UX** - users don't know whether to worry about these "failures"
- **False negatives** - SPI enabled test may fail even when SPI is working (checks wrong path on Pi 5)
- **Wasted effort** - users might try to fix things that don't need fixing

### Architecture

#### Backend-Specific Test Requirements

**rpi_ws281x Backend (Pi 1-4):**
- ✅ User in `gpio` group (required)
- ✅ SPI enabled in `/boot/config.txt` (required for Pi 3/4)
- ✅ SPI buffer size increased (recommended for >200 LEDs)
- ✅ core_freq settings (Pi 3: `core_freq=250`, Pi 4: `core_freq_min=500`)

**Adafruit NeoPixel SPI Backend (Pi 5):**
- ✅ User in `spi` group (required)
- ✅ SPI enabled - check `/boot/firmware/config.txt` OR `/dev/spidev0.0` exists (required)
- ❌ SPI buffer size (not applicable)
- ❌ core_freq settings (not applicable - SPI has hardware timing)

### Tasks

#### Task 5.1: Create backend-specific test definitions
- Define which tests apply to which backends
- Create test requirement specifications per backend
- Add Pi 5 specific checks (firmware config path, spi group)

**Commit:** `Wizard Enhancement - 5.1: Define backend-specific test requirements`

#### Task 5.2: Refactor wizard validation logic
- Make validators backend-aware
- Add Pi 5 detection and special handling
- Check `/boot/firmware/config.txt` on Pi 5 as fallback
- Update group membership checks based on backend

**Commit:** `Wizard Enhancement - 5.2: Implement backend-aware validation`

#### Task 5.3: Update wizard UI to show only relevant tests
- Filter tests based on detected Pi model and recommended backend
- Add explanatory text about which backend is being configured
- Show informational message about skipped tests
- Update test descriptions to be backend-specific

**Commit:** `Wizard Enhancement - 5.3: Update wizard UI for backend-aware tests`

#### Task 5.4: Add backend switching handling
- Handle case where user changes backend selection
- Re-validate with new backend's requirements
- Show/hide tests dynamically based on backend selection

**Commit:** `Wizard Enhancement - 5.4: Support backend switching in wizard`

#### Task 5.5: Update wizard tests
- Add tests for backend-aware validation logic
- Test Pi 5 specific checks
- Test filtering logic for different Pi models
- Test backend switching scenarios

**Commit:** `Wizard Enhancement - 5.5: Add tests for backend-aware wizard`

#### Task 5.6: Update documentation
- Document backend-specific requirements clearly
- Update wizard screenshots/guides
- Add troubleshooting for Pi 5 specific issues
- Document the wizard's backend-aware behavior

**Commit:** `Wizard Enhancement - 5.6: Update documentation for backend-aware wizard`

### Implementation Notes

**Pi 5 Specific Considerations:**
- Config file location: `/boot/firmware/config.txt` (not `/boot/config.txt`)
- Group membership: `spi` group (not `gpio` group)
- SPI verification: Check `/dev/spidev0.0` exists as fallback if config file check fails
- Skip buffer size and core_freq tests entirely

**Backward Compatibility:**
- Pi 1-4 users should see no change in wizard behavior
- Default to rpi_ws281x tests if backend cannot be determined
- All existing tests should continue to work for rpi_ws281x backend

**User Experience:**
- Clear indication of which backend is being configured
- Explanation of why certain tests are skipped
- Backend recommendation visible in wizard
- Option to manually override backend selection

**Milestone 5 Completion Criteria:**
- [ ] Wizard only shows relevant tests for detected hardware/backend
- [ ] Pi 5 users see correct tests (spi group, SPI enabled via device check)
- [ ] Pi 1-4 users see no change in wizard behavior
- [ ] Clear UI indicators of which backend is being configured
- [ ] All wizard tests passing for both backends
- [ ] Documentation updated with backend-specific requirements
- [ ] No false failures on any supported hardware

**Priority:** Medium (Enhancement)
**Estimated Effort:** 2-3 days

---

### Testing Strategy

**Unit Tests:**
- Test each backend implementation in isolation with mocks
- Test factory and registry logic
- Test settings migration
- Test configuration validation

**Integration Tests:**
- Test backend switching
- Test effects with different backends
- Test color accuracy and conversion

**Manual Testing:**
- Test on actual Raspberry Pi 5 hardware with real LED strips
- Verify all effects work correctly
- Test configuration UI usability
- Test migration from old settings

**Backward Compatibility:**
- Existing installations must continue working without changes
- Old settings format must migrate automatically
- Default backend (rpi_ws281x) must work exactly as before

---

### Risk Mitigation

**Risks:**
1. **Breaking existing functionality** - Mitigated by comprehensive tests and maintaining abstraction
2. **Dependency conflicts** - Mitigated by making Adafruit dependencies optional
3. **Performance degradation** - Mitigated by performance testing in Milestone 4
4. **User confusion** - Mitigated by clear documentation and wizard improvements

**Rollback Plan:**
If critical issues are discovered, the abstraction layer is designed to preserve the original rpi_ws281x behavior as default, allowing users to continue using the plugin even if new backends have issues.
