"""Business Functions"""
import logging
from time import sleep

from exceptions import MyFoxInitError
import schedule
from myfox.api import MyFoxApi
from myfox.api.devices.category import Category
from homeassistant.ha_discovery import (
    ha_discovery_alarm,
    ha_discovery_alarm_actions,
    ha_discovery_cameras,
    ha_discovery_devices,
    DEVICE_CAPABILITIES,
    ALARM_STATUS,
)
from business.mqtt import mqtt_publish
from mqtt import MQTTClient

LOGGER = logging.getLogger(__name__)


def ha_sites_config(
    api: MyFoxApi,
    mqtt_client: MQTTClient,
    mqtt_config: dict,
    homeassistant_config: dict,
    my_sites_id: list,
) -> None:
    """HA Site Config"""
    LOGGER.info("Looking for Sites")
    for site_id in my_sites_id:
        # Alarm Status
        my_sites = api.get_sites()
        for my_site in my_sites:
            if my_site.siteId == site_id:
                site = ha_discovery_alarm(
                    site=my_site,
                    mqtt_config=mqtt_config,
                    homeassistant_config=homeassistant_config,
                )
                # site_extended = ha_discovery_alarm_actions(
                #    site=my_site, mqtt_config=mqtt_config
                # )
                # configs = [site, site_extended]
                configs = [site]
                for site_config in configs:
                    mqtt_publish(
                        mqtt_client=mqtt_client,
                        topic=site_config.get("topic"),
                        payload=site_config.get("config"),
                        retain=True,
                    )
                    mqtt_client.client.subscribe(
                        site_config.get("config").get("command_topic")
                    )


def ha_devices_config(
    api: MyFoxApi,
    mqtt_client: MQTTClient,
    mqtt_config: dict,
    my_sites_id: list,
) -> None:
    """HA Devices Config"""
    LOGGER.info("Looking for Devices")
    for site_id in my_sites_id:
        my_devices = api.get_devices(site_id=site_id)

        api.get_devices_temperature(site_id=site_id)
        api.get_devices_light(site_id=site_id)
        api.get_devices_state(site_id=site_id)
        api.get_devices_other(site_id=site_id)
        api.get_devices_camera(site_id=site_id)
        api.get_scenarios(site_id=site_id)

        for device in my_devices:
            LOGGER.info(f"Configuring Device: {device.label}")
            settings = device.settings

            for keys in settings:
                for state in keys:
                    if not DEVICE_CAPABILITIES.get(state):
                        LOGGER.debug(f"No Config for {state}")
                        continue
                    device_config = ha_discovery_devices(
                        site_id=site_id,
                        device=device,
                        mqtt_config=mqtt_config,
                        sensor_name=state,
                    )
                    mqtt_publish(
                        mqtt_client=mqtt_client,
                        topic=device_config.get("topic"),
                        payload=device_config.get("config"),
                        retain=True,
                    )
                    if device_config.get("config").get("command_topic"):
                        mqtt_client.client.subscribe(
                            device_config.get("config").get("command_topic")
                        )

            if "Myfox HC2" in device.device_definition.get(
                "device_definition_label"
            ):
                LOGGER.info(
                    f"Found Central {device.device_definition.get('device_definition_label')}"
                )

            if "Myfox Security Camera" in device.device_definition.get(
                "device_definition_label"
            ):
                LOGGER.info(
                    f"Found Camera {device.device_definition.get('device_definition_label')}"
                )
                camera_config = ha_discovery_cameras(
                    site_id=site_id,
                    device=device,
                    mqtt_config=mqtt_config,
                )
                mqtt_publish(
                    mqtt_client=mqtt_client,
                    topic=camera_config.get("topic"),
                    payload=camera_config.get("config"),
                    retain=True,
                )
                reboot = ha_discovery_devices(
                    site_id=site_id,
                    device=device,
                    mqtt_config=mqtt_config,
                    sensor_name="reboot",
                )
                mqtt_publish(
                    mqtt_client=mqtt_client,
                    topic=reboot.get("topic"),
                    payload=reboot.get("config"),
                    retain=True,
                )
                mqtt_client.client.subscribe(
                    reboot.get("config").get("command_topic")
                )

                halt = ha_discovery_devices(
                    site_id=site_id,
                    device=device,
                    mqtt_config=mqtt_config,
                    sensor_name="halt",
                )
                mqtt_publish(
                    mqtt_client=mqtt_client,
                    topic=halt.get("topic"),
                    payload=halt.get("config"),
                    retain=True,
                )
                mqtt_client.client.subscribe(
                    halt.get("config").get("command_topic")
                )
                # Manual Snapshot
                device_config = ha_discovery_devices(
                    site_id=site_id,
                    device=device,
                    mqtt_config=mqtt_config,
                    sensor_name="snapshot",
                )
                mqtt_publish(
                    mqtt_client=mqtt_client,
                    topic=device_config.get("topic"),
                    payload=device_config.get("config"),
                    retain=True,
                )
                if device_config.get("config").get("command_topic"):
                    mqtt_client.client.subscribe(
                        device_config.get("config").get("command_topic")
                    )

            # Works with Websockets
            if "Télécommande 4 boutons" in device.device_definition.get(
                "device_definition_label"
            ):
                LOGGER.info(
                    f"Found {device.device_definition.get('device_definition_label')}"
                )
                key_fob_config = ha_discovery_devices(
                    site_id=site_id,
                    device=device,
                    mqtt_config=mqtt_config,
                    sensor_name="presence",
                )
                mqtt_publish(
                    mqtt_client=mqtt_client,
                    topic=key_fob_config.get("topic"),
                    payload=key_fob_config.get("config"),
                    retain=True,
                )

            if "Détecteur de mouvement" in device.device_definition.get(
                "device_definition_label"
            ) or "IntelliTAG" in device.device_definition.get(
                "device_definition_label"
            ):
                LOGGER.info(
                    f"Found Motion Sensor (PIR & IntelliTag) {device.device_definition.get('device_definition_label')}"
                )
                pir_config = ha_discovery_devices(
                    site_id=site_id,
                    device=device,
                    mqtt_config=mqtt_config,
                    sensor_name="motion_sensor",
                )
                mqtt_publish(
                    mqtt_client=mqtt_client,
                    topic=pir_config.get("topic"),
                    payload=pir_config.get("config"),
                    retain=True,
                )
                mqtt_publish(
                    mqtt_client=mqtt_client,
                    topic=pir_config.get("config").get("state_topic"),
                    payload={"motion_sensor": "False"},
                )


def update_sites_status(
    api: MyFoxApi,
    mqtt_client: MQTTClient,
    mqtt_config: dict,
    my_sites_id: list,
) -> None:
    """Uodate Devices Status (Including zone)"""
    LOGGER.info("Update Sites Status")
    for site_id in my_sites_id:
        try:
            status = api.get_site_status(site_id=site_id)
            LOGGER.info(f"Update {site_id} Status")
            # Push status to MQTT
            mqtt_publish(
                mqtt_client=mqtt_client,
                topic=f"{mqtt_config.get('topic_prefix', 'myFox2mqtt')}/{site_id}/state",
                payload={
                    "security_level": ALARM_STATUS.get(
                        status.get("payload").get("statusLabel"), "disarmed"
                    )
                },
                retain=False,
            )
        except Exception as exp:
            LOGGER.warning(f"Error while refreshing site: {exp}")
            continue


def update_devices_status(
    api: MyFoxApi,
    mqtt_client: MQTTClient,
    mqtt_config: dict,
    my_sites_id: list,
) -> None:
    """Update Devices Status (Including zone)"""
    LOGGER.info("Update Devices Status")
    for site_id in my_sites_id:
        try:
            my_devices = api.get_devices(site_id=site_id)
            for device in my_devices:
                settings = device.settings.get("global")
                status = device.status
                status_settings = {**status, **settings}

                # Convert Values to String
                keys_values = status_settings.items()
                payload = {str(key): str(value) for key, value in keys_values}

                # Push status to MQTT
                mqtt_publish(
                    mqtt_client=mqtt_client,
                    topic=f"{mqtt_config.get('topic_prefix', 'myFox2mqtt')}/{site_id}/{device.id}/state",
                    payload=payload,
                    retain=False,
                )
        except Exception as exp:
            LOGGER.warning(f"Error while refreshing devices: {exp}")
            continue


def update_camera_snapshot(
    api: MyFoxApi,
    mqtt_client: MQTTClient,
    mqtt_config: dict,
    my_sites_id: list,
) -> None:
    """Uodate Camera Snapshot"""
    LOGGER.info("Update Camera Snapshot")
    for site_id in my_sites_id:
        try:
            for category in [
                Category.MYFOX_CAMERA,
            ]:
                my_devices = api.get_devices(site_id=site_id, category=category)
                for device in my_devices:
                    api.camera_refresh_snapshot(
                        site_id=site_id, device_id=device.id
                    )
                    response = api.camera_snapshot(
                        site_id=site_id, device_id=device.id
                    )
                    if response.status_code == 200:
                        # Write image to temp file
                        path = f"{device.id}.jpeg"
                        with open(path, "wb") as tmp_file:
                            for chunk in response:
                                tmp_file.write(chunk)
                        # Read and Push to MQTT
                        with open(path, "rb") as tmp_file:
                            image = tmp_file.read()
                        byte_arr = bytearray(image)
                        topic = f"{mqtt_config.get('topic_prefix', 'myFox2mqtt')}/{site_id}/{device.id}/snapshot"
                        mqtt_publish(
                            mqtt_client=mqtt_client,
                            topic=topic,
                            payload=byte_arr,
                            retain=False,
                            is_json=False,
                        )

        except Exception as exp:
            LOGGER.warning(f"Error while refreshing snapshot: {exp}")
            continue
