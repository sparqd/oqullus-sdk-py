import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from oqullus_sdk import OqullusClient

INTEGRATION_WORKSPACE_PATH = "sparq.demo@proton.me/integration-test.ipynb"
INTEGRATION_EXPECTED_SUBSTRING = "test"
DOTENV_PATH = Path(__file__).resolve().parents[2] / ".env.test"
load_dotenv(dotenv_path=DOTENV_PATH, override=False)


def _get_env(name: str) -> str | None:
    return os.environ.get(name)


def _require_env(name: str) -> str:
    value = _get_env(name)
    if not value:
        pytest.skip(f"Missing integration env var: {name}")
    return value


@pytest.mark.integration
def test_client_credentials_fetch_file(tmp_path: Path) -> None:
    _require_env("WORKSPACE_API_BASE_URL")
    _require_env("OQULLUS_OAUTH_GRANT_TYPE")
    _require_env("OQULLUS_OAUTH_TOKEN_URL")
    _require_env("OQULLUS_OAUTH_CLIENT_ID")
    _require_env("OQULLUS_OAUTH_CLIENT_SECRET")

    client = OqullusClient()

    output = tmp_path / "test-integration.ipynb"
    written_path = client.workspace.fetch_file(INTEGRATION_WORKSPACE_PATH, dest_path=str(output))

    assert written_path == str(output)
    assert output.exists()
    assert INTEGRATION_EXPECTED_SUBSTRING in output.read_text(encoding="utf-8")
