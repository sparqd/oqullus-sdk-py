import os
from dataclasses import dataclass

import requests


@dataclass
class OAuthConfig:
    access_token_env: str = "OAUTH_ACCESS_TOKEN"
    refresh_token_env: str = "OAUTH_REFRESH_TOKEN"
    token_url_env: str = "OAUTH_TOKEN_URL"
    client_id_env: str = "OAUTH_CLIENT_ID"
    client_secret_env: str = "OAUTH_CLIENT_SECRET"


class OAuthTokenManager:
    def __init__(self, config: OAuthConfig, session: requests.Session) -> None:
        self.config = config
        self.session = session

    def _get_env(self, name: str) -> str:
        value = os.environ.get(name)
        if not value:
            raise RuntimeError(f"Missing required environment variable: {name}")
        return value

    def access_token(self) -> str:
        return self._get_env(self.config.access_token_env)

    def refresh_payload(self) -> dict:
        refresh_token = self._get_env(self.config.refresh_token_env)
        client_id = self._get_env(self.config.client_id_env)
        client_secret = self._get_env(self.config.client_secret_env)
        return {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "refresh_token": refresh_token,
            "client_secret": client_secret,
        }

    def refresh_tokens(self) -> dict:
        token_url = self._get_env(self.config.token_url_env)
        response = self.session.post(token_url, data=self.refresh_payload())
        response.raise_for_status()
        tokens = response.json()

        if "access_token" in tokens:
            os.environ[self.config.access_token_env] = tokens["access_token"]
        if "refresh_token" in tokens:
            os.environ[self.config.refresh_token_env] = tokens["refresh_token"]

        return tokens
