"""Business Functions"""
import logging
from datetime import datetime, timedelta
from time import sleep

from exceptions import MyFoxInitError
import schedule
from myfox.api import MyFoxApi
from myfox.api.devices.category import Category
from homeassistant.ha_discovery import (
    ha_discovery_alarm,
    ha_discovery_history,
    ha_discovery_alarm_actions,
    ha_discovery_cameras,
    ha_discovery_devices,
    ha_discovery_scenario_actions,
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
                    mqtt_client.client.subscribe(site_config.get("config").get("command_topic"))

                history = ha_discovery_history(
                    site=my_site,
                    mqtt_config=mqtt_config,
                )
                configs = [history]
                for history_config in configs:
                    mqtt_publish(
                        mqtt_client=mqtt_client,
                        topic=history_config.get("topic"),
                        payload=history_config.get("config"),
                        retain=True,
                    )

                # Scenarios
                scenarios = api.get_scenarios(site_id=site_id)
                for scenario in scenarios:
                    if scenario.get("typeLabel") == "onDemand":
                        LOGGER.info(f"Found Scenario onDemand {scenario.get('label')}: {scenario.get('scenarioId')}")
                        play_scenario = ha_discovery_scenario_actions(
                            site=my_site,
                            scenario=scenario,
                            mqtt_config=mqtt_config,
                        )
                        mqtt_publish(
                            mqtt_client=mqtt_client,
                            topic=play_scenario.get("topic"),
                            payload=play_scenario.get("config"),
                            retain=True,
                        )
                        mqtt_client.client.subscribe(play_scenario.get("config").get("command_topic"))


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
        temperature_devices = api.get_devices_temperature(site_id=site_id)
        light_devices = api.get_devices_light(site_id=site_id)
        state_devices = api.get_devices_state(site_id=site_id)
        other_devices = api.get_devices_other(site_id=site_id)
        camera_devices = api.get_devices_camera(site_id=site_id)
        shutter_devices = api.get_devices_shutter(site_id=site_id)
        socket_devices = api.get_devices_socket(site_id=site_id)

        for device in my_devices:
            LOGGER.info(f"Configuring Device: {device.label}")
            settings = device.settings
            for keys in settings:
                for state in settings[keys]:
                    sensor_name = f"{keys}_{state}"
                    if keys == "global":
                        sensor_name = state
                    if not DEVICE_CAPABILITIES.get(sensor_name):
                        LOGGER.debug(f"No Config for {sensor_name}")
                        continue

                    # make clean
                    clean_device_config = ha_discovery_devices(
                        site_id=site_id,
                        device=device,
                        mqtt_config=mqtt_config,
                        sensor_name=sensor_name,
                    )

                    mqtt_publish(
                        mqtt_client=mqtt_client,
                        topic=clean_device_config.get("topic"),
                        payload="",
                        retain=True,
                    )

                    # end make clean
                    device_config = ha_discovery_devices(
                        site_id=site_id,
                        device=device,
                        mqtt_config=mqtt_config,
                        sensor_name=sensor_name,
                    )
                    mqtt_publish(
                        mqtt_client=mqtt_client,
                        topic=device_config.get("topic"),
                        payload=device_config.get("config"),
                        retain=True,
                    )
                    if device_config.get("config").get("command_topic"):
                        mqtt_client.client.subscribe(device_config.get("config").get("command_topic"))

            if "Myfox HC2" in device.device_definition.get(
                "device_definition_label"
            ) or "Evology" in device.device_definition.get("device_definition_label"):
                LOGGER.info(f"Found Central {device.device_definition.get('device_definition_label')}")

            if "Myfox Security Camera" in device.device_definition.get("device_definition_label"):
                LOGGER.info(f"Found Camera {device.device_definition.get('device_definition_label')}")
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
                mqtt_client.client.subscribe(reboot.get("config").get("command_topic"))

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
                mqtt_client.client.subscribe(halt.get("config").get("command_topic"))
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
                    mqtt_client.client.subscribe(device_config.get("config").get("command_topic"))

            # Temperature
            for temperature_device in temperature_devices:
                if temperature_device.get("deviceId") == device.device_id:
                    LOGGER.info(
                        f"Found Temperature for {device.device_id}: {temperature_device.get('lastTemperature')}"
                    )
                    temperature = ha_discovery_devices(
                        site_id=site_id,
                        device=device,
                        mqtt_config=mqtt_config,
                        sensor_name="lastTemperature",
                    )
                    mqtt_publish(
                        mqtt_client=mqtt_client,
                        topic=temperature.get("topic"),
                        payload=temperature.get("config"),
                        retain=True,
                    )

            # Smoke
            for other_device in other_devices:
                if other_device.get("deviceId") == device.device_id:
                    LOGGER.info(f"Found Smoke for {device.device_id}: {other_device.get('state')}")
                    smoke = ha_discovery_devices(
                        site_id=site_id,
                        device=device,
                        mqtt_config=mqtt_config,
                        sensor_name="state",
                    )
                    mqtt_publish(
                        mqtt_client=mqtt_client,
                        topic=smoke.get("topic"),
                        payload=smoke.get("config"),
                        retain=True,
                    )

            # Shutter
            for shutter_device in shutter_devices:
                if shutter_device.get("deviceId") == device.device_id:
                    LOGGER.info(f"Found Shutter for {device.device_id}: {shutter_device.get('label')}")
                    shutter = ha_discovery_devices(
                        site_id=site_id,
                        device=device,
                        mqtt_config=mqtt_config,
                        sensor_name="shutter",
                    )
                    mqtt_publish(
                        mqtt_client=mqtt_client,
                        topic=shutter.get("topic"),
                        payload=shutter.get("config"),
                        retain=True,
                    )
                    mqtt_client.client.subscribe(shutter.get("config").get("command_topic"))

            # Sockets
            for socket_device in socket_devices:
                if socket_device.get("deviceId") == device.device_id:
                    LOGGER.info(f"Found Socket for {device.device_id}: {socket_device.get('label')}")
                    socket = ha_discovery_devices(
                        site_id=site_id,
                        device=device,
                        mqtt_config=mqtt_config,
                        sensor_name="socket",
                    )
                    mqtt_publish(
                        mqtt_client=mqtt_client,
                        topic=socket.get("topic"),
                        payload=socket.get("config"),
                        retain=True,
                    )
                    mqtt_client.client.subscribe(socket.get("config").get("command_topic"))

            # Works with Websockets
            if "Télécommande 4 boutons" in device.device_definition.get("device_definition_label"):
                LOGGER.info(f"Found {device.device_definition.get('device_definition_label')}")
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
            ) or "IntelliTAG" in device.device_definition.get("device_definition_label"):
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
            payload = {}
            events = api.get_site_history(site_id=site_id)
            for event in events:
                if event:
                    created_at = event.get("createdAt")
                    date_format = "%Y-%m-%dT%H:%M:%SZ"
                    created_at_date = datetime.strptime(created_at, date_format)
                    now = datetime.now()
                    if now - created_at_date < timedelta(seconds=70):
                        payload = f"{event.get('type')} {event.get('createdAt')} {event.get('label')}"
                        # Push status to MQTT
                        mqtt_publish(
                            mqtt_client=mqtt_client,
                            topic=f"{mqtt_config.get('topic_prefix', 'myFox2mqtt')}/{site_id}/history",
                            payload=payload,
                            retain=True,
                        )

        except Exception as exp:
            LOGGER.warning(f"Error while getting site history: {exp}")
            continue

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
            temperature_devices = api.get_devices_temperature(site_id=site_id)
            light_devices = api.get_devices_light(site_id=site_id)
            state_devices = api.get_devices_state(site_id=site_id)
            other_devices = api.get_devices_other(site_id=site_id)
            camera_devices = api.get_devices_camera(site_id=site_id)
            scenarios = api.get_scenarios(site_id=site_id)

            for device in my_devices:
                settings = device.settings

                # some device has not global values.
                if not settings:
                    continue

                keys_values = {}

                for keys in settings:
                    for state in settings[keys]:
                        sensor_name = f"{keys}_{state}"
                        if keys == "global":
                            sensor_name = state

                        keys_values[sensor_name] = settings[keys][state]

                # Temperature
                for temperature_device in temperature_devices:
                    if temperature_device.get("deviceId") == device.device_id:
                        keys_values["lastTemperature"] = temperature_device.get("lastTemperature")

                # Smoke
                for other_device in other_devices:
                    if other_device.get("deviceId") == device.device_id:
                        keys_values["state"] = other_device.get("state")

                payload = {str(key): str(value) for key, value in keys_values.items()}

                # Push status to MQTT
                mqtt_publish(
                    mqtt_client=mqtt_client,
                    topic=f"{mqtt_config.get('topic_prefix', 'myFox2mqtt')}/{site_id}/{device.device_id}/state",
                    payload=payload,
                    retain=True,
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
                    response = api.camera_snapshot(site_id=site_id, device_id=device.device_id)
                    if response.status_code == 200:
                        # Write image to temp file
                        path = f"{device.device_id}.jpeg"
                        with open(path, "wb") as tmp_file:
                            for chunk in response:
                                tmp_file.write(chunk)
                        # Read and Push to MQTT
                        with open(path, "rb") as tmp_file:
                            image = tmp_file.read()
                        byte_arr = bytearray(image)
                        topic = f"{mqtt_config.get('topic_prefix', 'myFox2mqtt')}/{site_id}/{device.device_id}/snapshot"
                        mqtt_publish(
                            mqtt_client=mqtt_client,
                            topic=topic,
                            payload=byte_arr,
                            retain=True,
                            is_json=False,
                        )

        except Exception as exp:
            LOGGER.warning(f"Error while refreshing snapshot: {exp}")
            continue
