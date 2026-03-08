"""Constants for the Sunshine Scooter integration."""
from __future__ import annotations

DOMAIN = "sunshine"

CONF_BASE_URL = "base_url"
DEFAULT_BASE_URL = "https://sunshine.rescoot.org"

ATTR_SCOOTER_ID = "scooter_id"
ATTR_VIN = "vin"
ATTR_DURATION = "duration"
ATTR_SOUND = "sound"
ATTR_STATE = "state"
ATTR_LATITUDE = "latitude"
ATTR_LONGITUDE = "longitude"
ATTR_ADDRESS = "address"

SERVICE_TRIGGER_ALARM = "trigger_alarm"
SERVICE_PLAY_SOUND = "play_sound"
SERVICE_BLINKERS = "blinkers"
SERVICE_OPEN_SEATBOX = "open_seatbox"
SERVICE_GET_STATE = "get_state"
SERVICE_SET_DESTINATION = "set_destination"
SERVICE_CLEAR_DESTINATION = "clear_destination"

SOUND_ALARM = "alarm"
SOUND_CHIRP = "chirp"
SOUND_FIND_ME = "find_me"

BLINKER_LEFT = "left"
BLINKER_RIGHT = "right"
BLINKER_BOTH = "both"
BLINKER_OFF = "off"

SCOOTER_COLOR_IMAGE_INDEX = {
    "black": 0,
    "white": 1,
    "pine": 2,
    "stone": 3,
    "coral": 4,
    "red": 5,
    "blue": 6,
    "eclipse": 7,
    "idioteque": 8,
}
