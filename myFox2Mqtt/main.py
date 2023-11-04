#!/usr/bin/env python3
"""MyFox 2 MQTT"""
import argparse
import logging
import threading
import time

from exceptions import MyFoxInitError
from myfox_2_mqtt import MyFox2Mqtt
from utils import close_and_exit, setup_logger, read_config_file
from mqtt import init_mqtt
from myfox.sso import init_sso
from myfox.api import MyFoxApi

VERSION = "2023.11.0"


def myfox_loop(config, mqtt_client, api):
    """MyFox 2 MQTT Loop"""
    try:
        myfox_api = MyFox2Mqtt(api=api, mqtt_client=mqtt_client, config=config)
        time.sleep(1)
        myfox_api.loop()
    except MyFoxInitError as exc:
        LOGGER.error(f"Force stopping Api {exc}")
        close_and_exit(myfox_api, 3)


if __name__ == "__main__":
    # Read Arguments
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("--verbose", "-v", action="store_true", help="verbose mode")
    PARSER.add_argument("--configuration", "-c", type=str, help="config file path")
    ARGS = PARSER.parse_args()
    DEBUG = ARGS.verbose
    CONFIG_FILE = ARGS.configuration

    # Setup Logger
    setup_logger(debug=DEBUG, filename="myFox2Mqtt.log")
    LOGGER = logging.getLogger(__name__)
    LOGGER.info(f"Starting MyFox2Mqtt {VERSION}")

    CONFIG = read_config_file(CONFIG_FILE)

    SSO = init_sso(config=CONFIG)
    API = MyFoxApi(sso=SSO)
    MQTT_CLIENT = init_mqtt(config=CONFIG, api=API)

    try:
        p1 = threading.Thread(
            target=myfox_loop,
            args=(
                CONFIG,
                MQTT_CLIENT,
                API,
            ),
        )

        p1.start()

        while True:
            if not p1.is_alive():
                LOGGER.warning("API is DEAD, restarting")
                p1 = threading.Thread(
                    target=myfox_loop,
                    args=(
                        CONFIG,
                        MQTT_CLIENT,
                        API,
                    ),
                )
                p1.start()

            time.sleep(1)

    except Exception as exp:
        LOGGER.error(f"Force stopping application {exp}")
