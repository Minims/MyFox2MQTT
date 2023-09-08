#!/usr/bin/env python3
"""MyFox 2 MQTT"""
import argparse
import logging
import threading
from functools import partial
from signal import SIGINT, SIGTERM, signal
import time

from exceptions import MyFoxInitError
from myfox_2_mqtt import MyFox2Mqtt
from utils import close_and_exit, setup_logger, read_config_file
from mqtt import init_mqtt
from myfox.sso import init_sso
from myfox.api import MyFoxApi
from myfox.websocket import MyFoxWebsocket

VERSION = "2023.9.3"


def myfox_loop(config, mqtt_client, api):
    """MyFox 2 MQTT Loop"""
    try:
        myfox_api = MyFox2Mqtt(api=api, mqtt_client=mqtt_client, config=config)
        time.sleep(1)
        myfox_api.loop()
    except MyFoxInitError as exc:
        LOGGER.error(f"Force stopping Api {exc}")
        close_and_exit(myfox_api, 3)


def myfox_wss_loop(sso, debug, config, mqtt_client, api):
    """MyFox WSS Loop"""
    try:
        wss = MyFoxWebsocket(sso=sso, debug=debug, config=config, mqtt_client=mqtt_client, api=api)
        wss.run_forever()
    except Exception as exc:
        LOGGER.error(f"Force stopping WebSocket {exc}")
        close_and_exit(wss, 3)


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

    # Trigger Ctrl-C
    signal(SIGINT, partial(close_and_exit, MyFox2Mqtt, 0))
    signal(SIGTERM, partial(close_and_exit, MyFox2Mqtt, 0))
    signal(SIGINT, partial(close_and_exit, MyFoxWebsocket, 0))
    signal(SIGTERM, partial(close_and_exit, MyFoxWebsocket, 0))

    try:
        p1 = threading.Thread(
            target=myfox_loop,
            args=(
                CONFIG,
                MQTT_CLIENT,
                API,
            ),
        )
        # p2 = threading.Thread(
        #     target=myfox_wss_loop,
        #     args=(
        #         SSO,
        #         DEBUG,
        #         CONFIG,
        #         MQTT_CLIENT,
        #         API,
        #     ),
        # )
        p1.start()
        # p2.start()
        # p2.join()
        # while True:
        #     if not p2.is_alive():
        #         p2 = threading.Thread(
        #             target=myfox_wss_loop,
        #             args=(
        #                 SSO,
        #                 DEBUG,
        #                 CONFIG,
        #                 MQTT_CLIENT,
        #                 API,
        #             ),
        #         )
        #         p2.start()
        #         p2.join()
    except Exception as exp:
        LOGGER.error(f"Force stopping application {exp}")
        # close_and_exit(MYFOX, 3)
