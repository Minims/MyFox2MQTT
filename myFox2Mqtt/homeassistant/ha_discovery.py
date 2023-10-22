"""HomeAssistant MQTT Auto Discover"""
import logging
from myfox.api.model import Site, Device

LOGGER = logging.getLogger(__name__)

ALARM_STATUS = {
    "partial": "armed_night",
    "disarmed": "disarmed",
    "armed": "armed_away",
    "triggered": "triggered",
}

DEVICE_CAPABILITIES = {
    "exit_delay": {
        "type": "number",
        "config": {"min": 0, "max": 120, "step": 5},
    },
    "entrance_delay": {
        "type": "number",
        "config": {"min": 0, "max": 120, "step": 5},
    },
    "image_detection_sensitivity": {
        "type": "number",
        "config": {"min": 0, "max": 100, "step": 1},
    },
    "shutter": {
        "type": "cover",
        "config": {"pl_open": "open", "pl_cls": "close", "pl_stop": "my", "optimistic": "true"},
    },
    "gate": {
        "type": "cover",
        "config": {"pl_open": "one", "pl_cls": "two", "optimistic": "true", "device_class": "gate"},
    },
    "socket": {
        "type": "switch",
        "config": {
            "pl_on": "on_socket",
            "pl_off": "off_socket",
        },
    },
    "image_detection_enabled": {
        "type": "switch",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "jamming_detection_enabled": {
        "type": "switch",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "silent_mode_enabled": {
        "type": "switch",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "enabled": {
        "type": "switch",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "armed_enabled": {
        "type": "switch",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "partial_enabled": {
        "type": "switch",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "disarmed_enabled": {
        "type": "switch",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "privacy_enabled": {
        "type": "switch",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "night_mode": {
        "type": "select",
        "config": {
            "options": ["automatic", "manual"],
        },
    },
    ## PROTECT ##
    "temperature": {
        "type": "sensor",
        "config": {
            "device_class": "temperature",
            "unit_of_measurement": "°C",
        },
    },
    "lastTemperature": {
        "type": "sensor",
        "config": {
            "device_class": "temperature",
            "unit_of_measurement": "°C",
        },
    },
    "light": {
        "type": "sensor",
        "config": {
            "device_class": "illuminance",
            "unit_of_measurement": "lx",
        },
    },
    "battery_level": {
        "type": "sensor",
        "config": {
            "device_class": "battery",
            "unit_of_measurement": "%",
        },
    },
    "battery_low": {
        "type": "binary_sensor",
        "config": {
            "device_class": "battery",
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "state": {
        "type": "binary_sensor",
        "config": {
            "device_class": "smoke",
            "pl_on": "1",
            "pl_off": "0",
        },
    },
    "rlink_quality": {
        "type": "sensor",
        "config": {
            "device_class": "signal_strength",
            "unit_of_measurement": "dB",
        },
    },
    "rlink_quality_percent": {
        "type": "sensor",
        "config": {
            "unit_of_measurement": "%",
        },
    },
    "sensitivity": {
        "type": "number",
        "config": {"min": 0, "max": 100},
    },
    "ambient_light_threshold": {
        "type": "number",
        "config": {"min": 0, "max": 255},
    },
    "lighting_duration": {
        "type": "number",
        "config": {"min": 0, "max": 900},
    },
    "sensitivity_IntelliTag": {
        "type": "number",
        "config": {"min": 1, "max": 9},
    },
    "night_vision": {
        "type": "select",
        "config": {
            "options": ["automatic"],
        },
    },
    "sensitivity_level": {
        "type": "select",
        "config": {
            "options": ["low", "medium", "high"],
        },
    },
    "support_type": {
        "type": "select",
        "config": {
            "options": [
                "slidedoor",
                "window",
                "externdoor",
                "interndoor",
                "slidewindow",
                "garage",
            ],
        },
    },
    "video_mode": {
        "type": "select",
        "config": {
            "options": ["FHD", "HD", "SD"],
        },
    },
    "smart_alarm_duration": {
        "type": "select",
        "config": {
            "options": ["30", "60", "90", "120"],
        },
    },
    "lighting_trigger": {
        "type": "select",
        "config": {
            "options": ["manual", "always"],
        },
    },
    "power_mode": {
        "type": "sensor",
        "config": {},
    },
    "wifi_ssid": {
        "type": "sensor",
        "config": {},
    },
    "fsk_level": {
        "type": "sensor",
        "config": {
            "device_class": "signal_strength",
            "unit_of_measurement": "dB",
        },
    },
    "ble_level": {
        "type": "sensor",
        "config": {
            "device_class": "signal_strength",
            "unit_of_measurement": "dB",
        },
    },
    "wifi_level": {
        "type": "sensor",
        "config": {
            "device_class": "signal_strength",
            "unit_of_measurement": "dB",
        },
    },
    "wifi_level_percent": {
        "type": "sensor",
        "config": {
            "unit_of_measurement": "%",
        },
    },
    "lora_quality_percent": {
        "type": "sensor",
        "config": {
            "unit_of_measurement": "%",
        },
    },
    "temperatureAt": {
        "type": "sensor",
        "config": {},
    },
    "last_online_at": {
        "type": "sensor",
        "config": {},
    },
    "last_offline_at": {
        "type": "sensor",
        "config": {},
    },
    "mounted_at": {
        "type": "sensor",
        "config": {},
    },
    "last_shutter_closed_at": {
        "type": "sensor",
        "config": {},
    },
    "last_shutter_opened_at": {
        "type": "sensor",
        "config": {},
    },
    "last_status_at": {
        "type": "sensor",
        "config": {},
    },
    "mfa_last_test_at": {
        "type": "sensor",
        "config": {},
    },
    "mfa_last_test_success_at": {
        "type": "sensor",
        "config": {},
    },
    "mfa_last_online_at": {
        "type": "sensor",
        "config": {},
    },
    "mfa_last_offline_at": {
        "type": "sensor",
        "config": {},
    },
    "mfa_last_connected_at": {
        "type": "sensor",
        "config": {},
    },
    "mfa_last_disconnected_at": {
        "type": "sensor",
        "config": {},
    },
    "lora_last_test_at": {
        "type": "sensor",
        "config": {},
    },
    "lora_last_test_success_at": {
        "type": "sensor",
        "config": {},
    },
    "lora_last_online_at": {
        "type": "sensor",
        "config": {},
    },
    "lora_test_on_going": {
        "type": "sensor",
        "config": {},
    },
    "lora_last_offline_at": {
        "type": "sensor",
        "config": {},
    },
    "lora_last_connected_at": {
        "type": "sensor",
        "config": {},
    },
    "lora_last_disconnected_at": {
        "type": "sensor",
        "config": {},
    },
    "last_check_in_state": {
        "type": "sensor",
        "config": {},
    },
    "last_check_out_state": {
        "type": "sensor",
        "config": {},
    },
    "keep_alive": {
        "type": "sensor",
        "config": {},
    },
    "rlink_state": {
        "type": "sensor",
        "config": {},
    },
    "battery_level_state": {
        "type": "sensor",
        "config": {},
    },
    "power_state": {
        "type": "sensor",
        "config": {},
    },
    "thresholdAcc": {
        "type": "sensor",
        "config": {},
    },
    "video_backend": {
        "type": "sensor",
        "config": {},
    },
    "gsm_antenna_in_use": {
        "type": "sensor",
        "config": {},
    },
    "mfa_quality_percent": {
        "type": "sensor",
        "config": {
            "unit_of_measurement": "%",
        },
    },
    "recalibration_required": {
        "type": "binary_sensor",
        "config": {
            "device_class": "problem",
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "cover_present": {
        "type": "binary_sensor",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "device_lost": {
        "type": "binary_sensor",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "push_to_talk_available": {
        "type": "binary_sensor",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "homekit_capable": {
        "type": "binary_sensor",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "lighting_state": {
        "type": "switch",
        "config": {
            "state_on": "True",
            "state_off": "False",
            "pl_on": "light_on",
            "pl_off": "light_off",
        },
    },
    "reboot": {
        "type": "button",
        "config": {"payload_press": "reboot"},
    },
    "halt": {
        "type": "button",
        "config": {"payload_press": "halt"},
    },
    "gate": {
        "type": "switch",
        "config": {
            "pl_on": "gate_open",
            "pl_off": "gate_close",
            "optimistic": "True",
        },
    },
    "garage": {
        "type": "switch",
        "config": {
            "pl_on": "garage_open",
            "pl_off": "garage_close",
            "optimistic": "True",
        },
    },
    "rolling_shutter": {
        "type": "switch",
        "config": {
            "pl_on": "rolling_shutter_up",
            "pl_off": "rolling_shutter_down",
            "optimistic": "True",
        },
    },
    "shutter_state": {
        "type": "switch",
        "config": {
            "state_on": "opened",
            "state_off": "closed",
            "pl_on": "shutter_open",
            "pl_off": "shutter_close",
        },
    },
    "detection_enabled": {
        "type": "switch",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "led_enabled": {
        "type": "switch",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "hdr_enabled": {
        "type": "switch",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "lighting_wired": {
        "type": "switch",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "siren_disabled": {
        "type": "switch",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "human_detect_enabled": {
        "type": "switch",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "siren_on_camera_detection_disabled": {
        "type": "switch",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "auto_rotate_enabled": {
        "type": "switch",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "sound_recording_enabled": {
        "type": "switch",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "sound_enabled": {
        "type": "switch",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "light_enabled": {
        "type": "switch",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "code_required_to_arm": {
        "type": "switch",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "auto_protect_enabled": {
        "type": "switch",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "night_mode_enabled": {
        "type": "switch",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "prealarm_enabled": {
        "type": "switch",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "sp_smoke_detector_alarm_muted": {
        "type": "binary_sensor",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "recalibrateable": {
        "type": "binary_sensor",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "is_full_gsm": {
        "type": "binary_sensor",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "sp_smoke_detector_error_chamber": {
        "type": "binary_sensor",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "sp_smoke_detector_no_disturb": {
        "type": "binary_sensor",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "sp_smoke_detector_role": {
        "type": "binary_sensor",
        "config": {
            "pl_on": "end_device",
            "pl_off": "coordinator",
        },
    },
    "sp_smoke_detector_smoke_detection": {
        "type": "binary_sensor",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
    "snapshot": {
        "type": "switch",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
            "optimistic": "True",
        },
    },
    "presence": {
        "type": "device_tracker",
        "config": {
            " payload_home": "home",
            " payload_not_home": "not_home",
        },
    },
    "motion_sensor": {
        "type": "binary_sensor",
        "config": {
            "pl_on": "True",
            "pl_off": "False",
        },
    },
}


def ha_discovery_alarm(site: Site, mqtt_config: dict, homeassistant_config: dict):
    """Auto Discover Alarm"""
    if homeassistant_config:
        code = homeassistant_config.get("code")
        code_arm_required = homeassistant_config.get("code_arm_required")
        code_disarm_required = homeassistant_config.get("code_disarm_required")
    else:
        code = None
        code_arm_required = None
        code_disarm_required = None

    site_config = {}

    site_info = {
        "identifiers": [site.siteId],
        "manufacturer": "MyFox",
        "model": "MyFox HC2",
        "name": "MyFox HC2",
        "sw_version": "MyFox2MQTT",
    }

    command_topic = f"{mqtt_config.get('topic_prefix', 'myFox2mqtt')}/{site.siteId}/command"
    site_config[
        "topic"
    ] = f"{mqtt_config.get('ha_discover_prefix', 'homeassistant')}/alarm_control_panel/{site.siteId}/alarm/config"
    site_config["config"] = {
        "name": site.label,
        "unique_id": f"{site.siteId}_{site.label}",
        "state_topic": f"{mqtt_config.get('topic_prefix', 'myFox2mqtt')}/{site.siteId}/state",
        "command_topic": command_topic,
        "payload_arm_away": "armed",
        "payload_arm_night": "partial",
        "payload_disarm": "disarmed",
        "value_template": "{{ value_json.security_level }}",
        "device": site_info,
    }
    if code and (isinstance(code, int)):
        site_config["config"]["code"] = code
    if not code_arm_required:
        site_config["config"]["code_arm_required"] = False
    if not code_disarm_required:
        site_config["config"]["code_disarm_required"] = False
    return site_config


def ha_discovery_history(site: Site, mqtt_config: dict):
    """Auto Discover History"""
    site_config = {}

    site_info = {
        "identifiers": [site.siteId],
        "manufacturer": "MyFox",
        "model": "MyFox HC2",
        "name": "MyFox HC2",
        "sw_version": "MyFox2MQTT",
    }

    site_config["topic"] = f"{mqtt_config.get('ha_discover_prefix', 'homeassistant')}/text/{site.siteId}/history/config"
    site_config["config"] = {
        "name": f"{site.label}_history",
        "unique_id": f"{site.siteId}_{site.label}_history",
        "state_topic": f"{mqtt_config.get('topic_prefix', 'myFox2mqtt')}/{site.siteId}/history",
        "device": site_info,
        "mode": "text",
        "command_topic": f"{mqtt_config.get('topic_prefix', 'myFox2mqtt')}/{site.siteId}/history",
        "min": 0,
        "max": 255,
    }
    return site_config


def ha_discovery_alarm_actions(site: Site, mqtt_config: dict):
    """Auto Discover Actions"""
    site_config = {}

    site_info = {
        "identifiers": [site.siteId],
        "manufacturer": "MyFox",
        "model": "MyFox HC2",
        "name": "MyFox HC2",
        "sw_version": "MyFox2MQTT",
    }

    command_topic = f"{mqtt_config.get('topic_prefix', 'myFox2mqtt')}/{site.siteId}/siren/command"
    site_config["topic"] = f"{mqtt_config.get('ha_discover_prefix', 'homeassistant')}/switch/{site.siteId}/siren/config"
    site_config["config"] = {
        "name": "Siren",
        "unique_id": f"{site.siteId}_{site.label}_siren",
        "command_topic": command_topic,
        "device": site_info,
        "pl_on": "panic",
        "pl_off": "stop",
    }

    return site_config


def ha_discovery_scenario_actions(site: Site, scenario: dict, mqtt_config: dict):
    """Auto Discover Scenarios Actions"""
    site_config = {}

    site_info = {
        "identifiers": [site.siteId],
        "manufacturer": "MyFox",
        "model": "MyFox HC2",
        "name": "MyFox HC2",
        "sw_version": "MyFox2MQTT",
    }

    command_topic = (
        f"{mqtt_config.get('topic_prefix', 'myFox2mqtt')}/{site.siteId}/{scenario.get('scenarioId')}/command"
    )
    site_config[
        "topic"
    ] = f"{mqtt_config.get('ha_discover_prefix', 'homeassistant')}/button/{site.siteId}/{scenario.get('scenarioId')}/config"
    site_config["config"] = {
        "name": scenario.get("label"),
        "unique_id": f"{site.siteId}_{scenario.get('label')}",
        "command_topic": command_topic,
        "device": site_info,
        "payload_press": "play_scenario",
    }

    return site_config


def ha_discovery_devices(
    site_id: str,
    device: Device,
    mqtt_config: dict,
    sensor_name: str,
):
    """Auto Discover Devices"""
    device_config = {}
    device_type = DEVICE_CAPABILITIES.get(sensor_name).get("type")

    device_info = {
        "identifiers": [device.device_id],
        "manufacturer": "MyFox",
        "model": device.device_definition.get("device_definition_label"),
        "name": device.label,
        "sw_version": "Unknown",
    }

    command_topic = (
        f"{mqtt_config.get('topic_prefix', 'myFox2mqtt')}/{site_id}/{device.device_id}/{sensor_name}/command"
    )
    device_config[
        "topic"
    ] = f"{mqtt_config.get('ha_discover_prefix', 'homeassistant')}/{device_type}/{site_id}_{device.device_id}/{sensor_name}/config"
    device_config["config"] = {
        "name": sensor_name,
        "unique_id": f"{device.device_id}_{sensor_name}",
        "state_topic": f"{mqtt_config.get('topic_prefix', 'myFox2mqtt')}/{site_id}/{device.device_id}/state",
        "value_template": "{{ value_json." + sensor_name + " }}",
        "device": device_info,
    }

    for config_entry in DEVICE_CAPABILITIES.get(sensor_name).get("config"):
        device_config["config"][config_entry] = DEVICE_CAPABILITIES.get(sensor_name).get("config").get(config_entry)
        # Specifiy for Intellitag Sensivity
        if device.device_definition.get("device_definition_label") == "IntelliTag" and sensor_name == "sensitivity":
            device_config["config"][config_entry] = (
                DEVICE_CAPABILITIES.get(f"{sensor_name}_{device.device_definition.get('label')}")
                .get("config")
                .get(config_entry)
            )
    if device_type in ("switch", "number", "select", "button"):
        device_config["config"]["command_topic"] = command_topic
    if device_type in ("cover"):
        device_config["config"]["command_topic"] = command_topic
        device_config["config"].pop("state_topic")
        device_config["config"].pop("value_template")
    if sensor_name == "snapshot":
        device_config["config"].pop("value_template")
    if sensor_name == "presence":
        device_config["config"][
            "state_topic"
        ] = f"{mqtt_config.get('topic_prefix', 'myFox2mqtt')}/{site_id}/{device.device_id}/presence"
    if sensor_name == "motion_sensor":
        device_config["config"][
            "state_topic"
        ] = f"{mqtt_config.get('topic_prefix', 'myFox2mqtt')}/{site_id}/{device.device_id}/pir"

    return device_config


def ha_discovery_cameras(
    site_id: str,
    device: Device,
    mqtt_config: dict,
):
    """Auto Discover Cameras"""
    camera_config = {}

    device_info = {
        "identifiers": [device.device_id],
        "manufacturer": "MyFox",
        "model": device.device_definition.get("device_definition_label"),
        "name": device.label,
        "sw_version": "Unknown",
    }

    camera_config[
        "topic"
    ] = f"{mqtt_config.get('ha_discover_prefix', 'homeassistant')}/camera/{site_id}_{device.device_id}/snapshot/config"
    camera_config["config"] = {
        "name": "snapshot",
        "unique_id": f"{device.device_id}_snapshot",
        "topic": f"{mqtt_config.get('topic_prefix', 'myFox2mqtt')}/{site_id}/{device.device_id}/snapshot",
        "device": device_info,
    }

    return camera_config
