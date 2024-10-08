""" MQTT Business"""

import json
import logging
from time import sleep

from homeassistant.ha_discovery import ALARM_STATUS
from paho.mqtt import client
from myfox.api import MyFoxApi, ACTION_LIST

LOGGER = logging.getLogger(__name__)
SUBSCRIBE_TOPICS = []


def mqtt_publish(mqtt_client, topic, payload, qos=0, retain=True, is_json=True):
    """MQTT publish"""
    if is_json:
        payload = json.dumps(payload, ensure_ascii=False).encode("utf8")
    mqtt_client.client.publish(topic, payload, qos=qos, retain=retain)


def update_device(api, mqtt_client, mqtt_config, site_id, device_id):
    """Update MQTT data for a device"""
    LOGGER.info(f"Live Update device {device_id}")
    try:
        device = api.get_device(site_id=site_id, device_id=device_id)
        settings = device.settings

        # Convert Values to String
        keys_values = settings.items()
        payload = {str(key): str(value) for key, value in keys_values}
        # Push status to MQTT
        mqtt_publish(
            mqtt_client=mqtt_client,
            topic=f"{mqtt_config.get('topic_prefix', 'myFox2mqtt')}/{site_id}/{device.device_id}/state",
            payload=payload,
            retain=True,
        )
    except Exception as exp:
        LOGGER.warning(f"Error while refreshing {device.label}: {exp}")


def update_site(api, mqtt_client, mqtt_config, site_id):
    """Update MQTT data for a site"""
    LOGGER.info(f"Live Update site {site_id}")
    try:
        status = api.get_site_status(site_id=site_id)
        LOGGER.info(f"Update {site_id} Status")
        # Push status to MQTT
        mqtt_publish(
            mqtt_client=mqtt_client,
            topic=f"{mqtt_config.get('topic_prefix', 'myFox2mqtt')}/{site_id}/state",
            payload={"security_level": ALARM_STATUS.get(status.get("payload").get("statusLabel"), "disarmed")},
            retain=True,
        )
    except Exception as exp:
        LOGGER.warning(f"Error while refreshing site {site_id}: {exp}")


def consume_mqtt_message(msg, mqtt_config: dict, api: MyFoxApi, mqtt_client: client):
    """Compute MQTT received message"""
    try:
        text_payload = msg.payload.decode("UTF-8").lower()
        LOGGER.info(f"MQTT Payload: {text_payload}")
        # Manage Boolean
        if text_payload == "True":
            text_payload = bool(True)

        if text_payload == "False":
            text_payload = bool(False)

        # Manage Alarm Status
        if text_payload in ALARM_STATUS:
            LOGGER.info(f"Security Level update ! Setting to {text_payload}")
            try:
                site_id = msg.topic.split("/")[1]
                LOGGER.debug(f"Site ID: {site_id}")
            except Exception as exp:
                LOGGER.warning(f"Unable to reteive Site ID: {site_id}: {exp}")
            # Update Alarm via API
            api.update_security_level(site_id=site_id, security_level=text_payload)
            # Read updated Alarm Status
            sleep(2)
            update_site(
                api=api,
                mqtt_client=mqtt_client,
                mqtt_config=mqtt_config,
                site_id=site_id,
            )

        # Manage Shutter
        elif text_payload in ["open", "close", "my"]:
            site_id = msg.topic.split("/")[1]
            device_id = msg.topic.split("/")[2]
            LOGGER.info(f"{text_payload} Shutter on {site_id} / {device_id}")
            api.shutter_action_device(site_id=site_id, device_id=device_id, action=text_payload)

        # Manage Gate
        elif text_payload in ["one", "two"]:
            site_id = msg.topic.split("/")[1]
            device_id = msg.topic.split("/")[2]
            LOGGER.info(f"{text_payload} Gate on {site_id} / {device_id}")
            api.gate_action_device(site_id=site_id, device_id=device_id, action=text_payload)

        # Manage Socket
        elif text_payload in ["on_socket", "off_socket"]:
            site_id = msg.topic.split("/")[1]
            device_id = msg.topic.split("/")[2]
            action = text_payload.split("_")[0]
            LOGGER.info(f"{action} Socket on {site_id} / {device_id}")
            api.socket_action_device(site_id=site_id, device_id=device_id, action=action)

        # Manage Scenarios
        elif text_payload in ["play_scenario", "enable_scenario", "disbale_scenario"]:
            site_id = msg.topic.split("/")[1]
            scenario_id = msg.topic.split("/")[2]
            action = text_payload.split("_")[0]
            LOGGER.info(f"{text_payload} Scenario on {site_id} / {scenario_id}")
            api.scenario_action(site_id=site_id, scenario_id=scenario_id, action=action)

        # Manage Siren
        elif text_payload == "panic":
            site_id = msg.topic.split("/")[1]
            LOGGER.info(f"Start the Siren On Site ID {site_id}")
            api.trigger_alarm(site_id=site_id, mode="alarm")

        elif text_payload == "stop":
            site_id = msg.topic.split("/")[1]
            LOGGER.info(f"Stop the Siren On Site ID {site_id}")
            api.stop_alarm(site_id=site_id)

        # Manage Actions
        elif text_payload in ACTION_LIST:
            site_id = msg.topic.split("/")[1]
            device_id = msg.topic.split("/")[2]
            if device_id:
                LOGGER.info(f"Message received for Site ID: {site_id}, Device ID: {device_id}, Action: {text_payload}")
                action_device = api.action_device(
                    site_id=site_id,
                    device_id=device_id,
                    action=text_payload,
                )
                LOGGER.debug(action_device)
                # Read updated device
                sleep(2)
                update_device(
                    api=api,
                    mqtt_client=mqtt_client,
                    mqtt_config=mqtt_config,
                    site_id=site_id,
                    device_id=device_id,
                )
            else:
                LOGGER.info(f"Message received for Site ID: {site_id}, Action: {text_payload}")

        # Manage Manual Snapshot
        elif msg.topic.split("/")[3] == "snapshot":
            site_id = msg.topic.split("/")[1]
            device_id = msg.topic.split("/")[2]
            if text_payload == "True":
                LOGGER.info("Manual Snapshot")
                response = api.camera_snapshot(site_id=site_id, device_id=device_id)
                if response.status_code == 200:
                    # Write image to temp file
                    path = f"{device_id}.jpeg"
                    with open(path, "wb") as snapshot_file:
                        for chunk in response:
                            snapshot_file.write(chunk)
                    # Read and Push to MQTT
                    snapshot_file = open(path, "rb")
                    image = snapshot_file.read()
                    byte_array = bytearray(image)
                    topic = f"{mqtt_config.get('topic_prefix', 'myFox2mqtt')}/{site_id}/{device_id}/snapshot"
                    mqtt_publish(
                        mqtt_client,
                        topic,
                        byte_array,
                        retain=True,
                        is_json=False,
                    )

        # Manage Settings update
        else:
            site_id = msg.topic.split("/")[1]
            device_id = msg.topic.split("/")[2]
            setting = msg.topic.split("/")[3]
            device = api.get_device(site_id=site_id, device_id=device_id)
            LOGGER.info(f"Message received for Site ID: {site_id}, Device ID: {device_id}, Setting: {setting}")
            settings = device.settings
            settings["global"][setting] = text_payload
            api.update_device(
                site_id=site_id,
                device_id=device_id,
                device_label=device.label,
                settings=settings,
            )
            # Read updated device
            sleep(2)
            update_device(
                api=api,
                mqtt_client=mqtt_client,
                mqtt_config=mqtt_config,
                site_id=site_id,
                device_id=device_id,
            )

    except Exception as exp:
        LOGGER.error(f"Error when processing message: {exp}")
