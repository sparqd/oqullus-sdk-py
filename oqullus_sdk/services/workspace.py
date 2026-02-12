import os
import tempfile
from typing import Optional

import requests

from oqullus_sdk.oauth import OAuthTokenManager


class WorkspaceService:
    def __init__(
        self,
        base_url: str,
        session: requests.Session,
        oauth: OAuthTokenManager,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = session
        self.oauth = oauth

    def _get_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.oauth.access_token()}"}

    def fetch_file(
        self,
        path: str,
        dest_path: Optional[str] = None,
        chunk_size: int = 8192,
        refresh_on_401: bool = True,
    ) -> str:
        url = f"{self.base_url}/workspace/file/content/by_path"
        if dest_path is None:
            filename = os.path.basename(path) or "workspace-file"
            dest_path = os.path.join(tempfile.gettempdir(), filename)

        response = self.session.get(
            url,
            headers=self._get_headers(),
            params={"path": path},
            stream=True,
        )

        if response.status_code == 401 and refresh_on_401:
            self.oauth.refresh_tokens()
            response = self.session.get(
                url,
                headers=self._get_headers(),
                params={"path": path},
                stream=True,
            )

        response.raise_for_status()

        with open(dest_path, "wb") as handle:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    handle.write(chunk)

        return dest_path
