import os
from typing import Optional

import requests

from oqullus_sdk.oauth import OAuthConfig, OAuthTokenManager
from oqullus_sdk.services.workspace import WorkspaceService


class OqullusClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        oauth: OAuthConfig | None = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        if base_url is None:
            base_url = os.environ.get("WORKSPACE_API_BASE_URL")
            if not base_url:
                raise RuntimeError("Missing required environment variable: WORKSPACE_BASE_URL")
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.oauth = OAuthTokenManager(oauth or OAuthConfig(), self.session)

        self.workspace = WorkspaceService(
            base_url=self.base_url,
            session=self.session,
            oauth=self.oauth,
        )
