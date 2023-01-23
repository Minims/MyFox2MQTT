"""MyFox Sso"""
import base64
import json
import logging
import os
from json import JSONDecodeError
from typing import Any, Callable, Dict, List, Optional, Union

from exceptions import MyFoxInitError
from oauthlib.oauth2 import LegacyApplicationClient, TokenExpiredError
from requests import Response
from requests_oauthlib import OAuth2Session

LOGGER = logging.getLogger(__name__)

MYFOX_TOKEN = "https://api.myfox.me/oauth2/token"
CACHE_PATH = "token.json"


def read_token_from_file(cache_path: dict = CACHE_PATH) -> Dict:
    """Retrieve a token from a file"""
    try:
        with open(file=cache_path, mode="r", encoding="utf8") as cache:
            return json.loads(cache.read())
    except IOError:
        return {}


def write_token_to_file(token, cache_path: dict = CACHE_PATH) -> None:
    """Write a token into a file"""
    with open(file=cache_path, mode="w", encoding="utf8") as cache:
        cache.write(json.dumps(token))


class MyFoxSso:
    """MyFox Sso"""

    def __init__(
        self,
        username: str,
        password: str,
        client_id: str,
        client_secret: str,
        token: Optional[Dict[str, str]] = read_token_from_file(),
        token_updater: Optional[Callable[[str], None]] = write_token_to_file,
    ):

        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_updater = token_updater

        extra = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        self._oauth = OAuth2Session(
            client=LegacyApplicationClient(client_id=self.client_id),
            token=token,
            auto_refresh_kwargs=extra,
            token_updater=token_updater,
        )
        self._oauth.headers["User-Agent"] = "MyFox"

    def request_token(
        self,
    ) -> Dict[str, str]:
        """Generic method for fetching a MyFox access token.

        Returns:
            Dict[str, str]: Token
        """
        LOGGER.info("Requesting Token")
        return self._oauth.fetch_token(
            MYFOX_TOKEN,
            username=self.username,
            password=self.password,
            client_id=self.client_id,
            client_secret=self.client_secret,
            include_client_id=True,
        )

    def refresh_tokens(self) -> Dict[str, Union[str, int]]:
        """Refresh and return new Somfy tokens.

        Returns:
            Dict[str, Union[str, int]]: Token
        """
        LOGGER.info("Refreshing Token")
        token = self._oauth.refresh_token(MYFOX_TOKEN)

        if self.token_updater is not None:
            self.token_updater(token)

        LOGGER.info(f"New Token: {token}")
        return token


def init_sso(config: dict) -> None:
    """Init SSO

    Args:
        config (dict): Global Configuration

    Raises:
        MyFoxInitError: Unable to init
    """
    logging.info("Init SSO")
    username = config.get("myfox").get("username")
    password = config.get("myfox").get("password")
    client_id = config.get("myfox").get("client_id")
    client_secret = config.get("myfox").get("client_secret")
    if username is None or password is None:
        raise MyFoxInitError("Username/Password is missing in config")

    sso = MyFoxSso(
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
    )
    if not os.path.isfile(CACHE_PATH):
        token = sso.request_token()
        write_token_to_file(token)
    return sso
