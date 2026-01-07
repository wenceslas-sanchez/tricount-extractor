import json
import uuid
from typing import Any
from dataclasses import dataclass

import httpx

from tricount_extractor.client.keys import generate_public_rsa_key

BASE_URL = "https://api.tricount.bunq.com"
ACCESS_TOKEN_URL = f"{BASE_URL}/v1/session-registry-installation"
USER_URL = f"{BASE_URL}/v1/user"
USER_AGENT = "com.bunq.tricount.android:RELEASE:7.0.7:3174:ANDROID:13:C"


class TricountClient:
    def __init__(self):
        self._application_id = self._generate_application_id()

        self._access_token: AccessToken | None = None

    def __enter__(self):
        self._authenticate()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._access_token = None
        return None

    def get_registry(self, public_identifier_token: str) -> httpx.Response:
        with httpx.Client() as client:
            response = client.get(
                self._registry_url,
                params=self._registry_params(public_identifier_token),
                headers=self._get_headers_with_access_token(),
            )
            response.raise_for_status()
            return response

    @property
    def _registry_url(self) -> str:
        if self._access_token is None:
            msg = "need to authenticate before generating registry URL"
            raise MissingAccessToken(msg)
        return f"{USER_URL}/{self._access_token.user_id}/registry"

    @staticmethod
    def _registry_params(public_identifier_token: str) -> dict[str, str]:
        return {"public_identifier_token": public_identifier_token}

    def _authenticate(self) -> None:
        with httpx.Client() as client:
            response = client.post(
                ACCESS_TOKEN_URL,
                json=self._generate_access_token_payload(),
                headers=self._get_headers(),
            )
            response.raise_for_status()
        self._access_token = AccessToken.from_response(response)

    def _generate_access_token_payload(self):
        return {
            "app_installation_uuid": self._application_id,
            "client_public_key": generate_public_rsa_key(),
            "device_description": "Android",
        }

    @staticmethod
    def _generate_application_id() -> str:
        return str(uuid.uuid4())

    def _get_headers(self) -> dict[str, str]:
        return {
            "User-Agent": USER_AGENT,
            "app-id": self._application_id,
            "X-Bunq-Client-Request-Id": str(uuid.uuid4()),
            "Content-Type": "application/json",
        }

    def _get_headers_with_access_token(self) -> dict[str, str]:
        if self._access_token is None:
            msg = "need to authenticate before generating header"
            raise MissingAccessToken(msg)
        headers = self._get_headers()
        headers["X-Bunq-Client-Authentication"] = self._access_token.access_token

        return headers


@dataclass(frozen=True)
class AccessToken:
    access_token: str
    user_id: str

    @classmethod
    def from_response(cls, response: httpx.Response) -> "AccessToken":
        access_token, user_id = cls._parse_response(response)
        if (access_token is None) or (user_id is None):
            msg = "missing the access token and/or the user ID"
            raise ValueError(msg)

        return cls(access_token, user_id)

    @staticmethod
    def _parse_response(response: httpx.Response):
        response_data = response.json()
        if (response_items := response_data.get("Response")) is None:
            msg = "no response found"
            raise ValueError(msg)

        access_token = None
        user_id = None
        for item in response_items:
            if "Token" in item:
                access_token = item["Token"]["token"]
            elif "UserPerson":
                user_id = item["UserPerson"]["id"]
            continue

        return access_token, user_id


class MissingAccessToken(Exception):
    """No access token available"""
