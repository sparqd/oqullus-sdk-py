import os
import time
from dataclasses import dataclass
from typing import Optional

import requests
from tenacity import retry

from oqullus_sdk.retry import retry_policy, stop_policy, wait_policy

@dataclass
class OAuthConfig:
    grant_type: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_url: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    scope: Optional[str] = None
    audience: Optional[str] = None
    access_token_env: str = "OAUTH_ACCESS_TOKEN"
    refresh_token_env: str = "OAUTH_REFRESH_TOKEN"
    token_url_env: str = "OAUTH_TOKEN_URL"
    client_id_env: str = "OAUTH_CLIENT_ID"
    client_secret_env: str = "OAUTH_CLIENT_SECRET"
    grant_type_env: str = "OAUTH_GRANT_TYPE"
    scope_env: str = "OAUTH_SCOPE"
    audience_env: str = "OAUTH_AUDIENCE"


class OAuthTokenManager:
    def __init__(self, config: OAuthConfig, session: requests.Session) -> None:
        self.config = config
        self.session = session
        self._cached_access_token: Optional[str] = config.access_token
        self._cached_access_token_expiry_ts: float = 0.0

    def _get_optional(self, explicit_value: Optional[str], env_name: str) -> Optional[str]:
        if explicit_value:
            return explicit_value
        return os.environ.get(env_name)

    def _required(self, explicit_value: Optional[str], env_name: str) -> str:
        value = self._get_optional(explicit_value, env_name)
        if not value:
            raise RuntimeError(f"Missing required OAuth setting: {env_name}")
        return value

    def access_token(self) -> str:
        now = time.time()
        if self._cached_access_token and now < self._cached_access_token_expiry_ts:
            return self._cached_access_token

        token = self._get_optional(self.config.access_token, self.config.access_token_env)
        if token and self.grant_type() != "client_credentials":
            self._cached_access_token = token
            self._cached_access_token_expiry_ts = now + 300
            return token

        tokens = self.refresh_tokens()
        access_token = tokens.get("access_token")
        if not access_token:
            raise RuntimeError("OAuth token response missing 'access_token'")
        return str(access_token)

    def grant_type(self) -> str:
        grant_type = self._get_optional(self.config.grant_type, self.config.grant_type_env)
        resolved = (grant_type or "refresh_token").strip()
        if resolved not in {"refresh_token", "client_credentials"}:
            raise RuntimeError(
                f"Unsupported OAuth grant type '{resolved}'. "
                "Expected 'refresh_token' or 'client_credentials'."
            )
        return resolved

    def refresh_payload(self) -> dict:
        refresh_token = self._required(self.config.refresh_token, self.config.refresh_token_env)
        client_id = self._required(self.config.client_id, self.config.client_id_env)
        client_secret = self._required(self.config.client_secret, self.config.client_secret_env)
        return {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "refresh_token": refresh_token,
            "client_secret": client_secret,
        }

    def client_credentials_payload(self) -> dict:
        payload = {
            "grant_type": "client_credentials",
            "client_id": self._required(self.config.client_id, self.config.client_id_env),
            "client_secret": self._required(self.config.client_secret, self.config.client_secret_env),
        }
        scope = self._get_optional(self.config.scope, self.config.scope_env)
        audience = self._get_optional(self.config.audience, self.config.audience_env)
        if scope:
            payload["scope"] = scope
        if audience:
            payload["audience"] = audience
        return payload

    def token_payload(self) -> dict:
        if self.grant_type() == "client_credentials":
            return self.client_credentials_payload()
        return self.refresh_payload()

    def refresh_tokens(self) -> dict:
        token_url = self._required(self.config.token_url, self.config.token_url_env)
        response = self._request_token_with_retry(token_url, self.token_payload())
        response.raise_for_status()
        tokens = response.json()

        if "access_token" in tokens:
            access_token = str(tokens["access_token"])
            expires_in = int(tokens.get("expires_in", 300))
            self._cached_access_token = access_token
            self._cached_access_token_expiry_ts = time.time() + max(60, expires_in - 60)
            os.environ[self.config.access_token_env] = access_token
        if "refresh_token" in tokens:
            os.environ[self.config.refresh_token_env] = str(tokens["refresh_token"])

        return tokens

    @retry(
        reraise=True,
        retry=retry_policy,
        stop=stop_policy,
        wait=wait_policy,
    )
    def _request_token_with_retry(self, token_url: str, payload: dict) -> requests.Response:
        response = self.session.post(token_url, data=payload)
        response.raise_for_status()
        return response
