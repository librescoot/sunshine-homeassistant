# Sunshine Scooter Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=librescoot&repository=sunshine-homeassistant&category=integration)

Part of the [Librescoot](https://librescoot.org/) open-source platform.

This custom component integrates Sunshine scooters with Home Assistant, providing full control and monitoring capabilities.

## Features

Each scooter is added as a device using its name as the friendly name (falls back to VIN if unnamed). The odometer is tracked as a long-term statistic.

### Entities Created per Scooter

#### Device Tracker
- **Location**: GPS tracking with map visualization

#### Sensors
- **Battery Level**: Current battery percentage
- **Speed**: Current speed in km/h
- **Odometer**: Total distance traveled in km (long-term statistic)
- **Status**: Current scooter state
- **Alarm State**: Current alarm state
- **Kickstand**: Kickstand position
- **Seatbox**: Seatbox state
- **Last Seen**: Timestamp of last communication
- **Battery Voltage**: Main battery voltage
- **Battery Health**: Main battery state of health
- **Battery Cycle Count**: Main battery charge cycles
- **Battery State**: Main battery state
- **Battery 1 Level/Voltage/Health/Cycle Count/State**: Second battery (if present)
- **Aux Battery Level/Voltage**: Auxiliary battery
- **CBB Battery Level/Health/Cycle Count**: CBB battery
- **Engine Temperature**: Motor temperature
- **Motor RPM**: Motor speed
- **Signal Quality**: Cellular signal quality

#### Binary Sensors
- **Online**: Scooter connectivity status
- **Alarm Triggered**: Whether the alarm is currently triggered

#### Switches
- **Lock**: Lock/unlock the scooter
- **Alarm Armed**: Arm/disarm the alarm system

#### Select Controls
- **Blinkers**: Control turn signals (off, left, right, both)
- **Play Sound**: Play various sounds (alarm, chirp, find_me)

#### Buttons
- **Honk**: Activate horn
- **Locate**: Find your scooter
- **Ping**: Check connectivity
- **Open Seatbox**: Open storage compartment
- **Request State**: Get fresh telemetry data
- **Alarm (5s)**: Quick 5-second alarm
- **Arm Alarm**: Arm the alarm system
- **Disarm Alarm**: Disarm the alarm system
- **Stop Alarm**: Stop an active alarm
- **Hibernate**: Put scooter into hibernation mode

### Services

- `sunshine.trigger_alarm`: Trigger alarm with custom duration
- `sunshine.get_state`: Request fresh telemetry data
- `sunshine.set_destination`: Set a navigation destination (latitude, longitude, optional address)
- `sunshine.clear_destination`: Clear the current navigation destination

## Installation

### Option 1: HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=librescoot&repository=sunshine-homeassistant&category=integration)

1. Click the button above to add this repository to HACS
2. Or manually add the repository:
   - Open HACS in Home Assistant
   - Go to "Integrations"
   - Click the three dots menu → "Custom repositories"
   - Add `https://github.com/librescoot/sunshine-homeassistant` as an Integration
3. Search for "Sunshine Scooter" in HACS
4. Click "Download"
5. Restart Home Assistant
6. Go to Settings → Devices & Services → Add Integration
7. Search for "Sunshine Scooter"
8. Enter your API token (get from https://rescoot.org/account#new_token_form)

### Option 2: Manual Installation

1. Copy the `custom_components/sunshine` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "Sunshine Scooter"
5. Enter your API token (get from https://rescoot.org/account#new_token_form)

## Configuration

The integration is configured through the UI. You'll need:
- **API Token**: Your Sunshine API bearer token
- **Base URL** (optional): Default is https://sunshine.rescoot.org

## Example Automations

### Zone-based Locking
```yaml
automation:
  - alias: "Auto-lock scooter when leaving home"
    trigger:
      - platform: zone
        entity_id: device_tracker.YOUR_SCOOTER_location
        zone: zone.home
        event: leave
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.YOUR_SCOOTER_lock
```

### Low Battery Alert
```yaml
automation:
  - alias: "Low battery notification"
    trigger:
      - platform: numeric_state
        entity_id: sensor.YOUR_SCOOTER_battery_level
        below: 20
    action:
      - service: notify.mobile_app
        data:
          message: "Scooter battery is low: {{ states('sensor.YOUR_SCOOTER_battery_level') }}%"
```

## License

This project is dual-licensed. The source code is available under the
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].
The maintainers reserve the right to grant separate licenses for commercial distribution; please contact the maintainers to discuss commercial licensing.

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
