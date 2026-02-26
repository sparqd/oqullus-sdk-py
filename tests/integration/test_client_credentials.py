import os
from pathlib import Path

import pytest

from oqullus_sdk import OAuthConfig, OqullusClient

INTEGRATION_WORKSPACE_PATH = "sparq.demo@proton.me/integration-test.ipynb"
INTEGRATION_EXPECTED_SUBSTRING = "test"
DOTENV_PATH = Path(__file__).resolve().parents[2] / ".env.test"


def _load_env_test_file() -> None:
    if not DOTENV_PATH.exists():
        return

    for raw_line in DOTENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and value and key not in os.environ:
            os.environ[key] = value


_load_env_test_file()


def _get_env(name: str) -> str | None:
    return os.environ.get(name)


def _require_env(name: str) -> str:
    value = _get_env(name)
    if not value:
        pytest.skip(f"Missing integration env var: {name}")
    return value


@pytest.mark.integration
def test_client_credentials_fetch_file(tmp_path: Path) -> None:
    base_url = _require_env("WORKSPACE_API_BASE_URL")
    token_url = _require_env("OQULLUS_INTEGRATION_TOKEN_URL")
    client_id = _require_env("OQULLUS_INTEGRATION_CLIENT_ID")
    client_secret = _require_env("OQULLUS_INTEGRATION_CLIENT_SECRET")

    client = OqullusClient(
        base_url=base_url,
        oauth=OAuthConfig(
            grant_type="client_credentials",
            token_url=token_url,
            client_id=client_id,
            client_secret=client_secret,
            scope=_get_env("OQULLUS_INTEGRATION_SCOPE"),
            audience=_get_env("OQULLUS_INTEGRATION_AUDIENCE"),
        ),
    )

    output = tmp_path / "test-integration.ipynb"
    written_path = client.workspace.fetch_file(INTEGRATION_WORKSPACE_PATH, dest_path=str(output))

    assert written_path == str(output)
    assert output.exists()
    assert INTEGRATION_EXPECTED_SUBSTRING in output.read_text(encoding="utf-8")
