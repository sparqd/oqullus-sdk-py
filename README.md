# oqullus-sdk-py

Minimal SDK for fetching workspace files in a Jupyter runtime.

The SDK retries transient HTTP/network failures (connection issues, `429`, `5xx`)
using exponential backoff.

## Usage

```python
from oqullus_sdk import OqullusClient

client = OqullusClient()

local_path = client.workspace.fetch_file(
    "my_workspace@example.com/data.csv"
)
print(f"File written to: {local_path}")
```

### Service account usage (client credentials)

```python
from oqullus_sdk import OqullusClient, OAuthConfig

client = OqullusClient(
    oauth=OAuthConfig(
        grant_type="client_credentials",
        token_url="https://issuer.example.com/oauth/token",
        client_id="<service-account-client-id>",
        client_secret="<service-account-client-secret>",
        scope="workspace:read",
    )
)
```

The SDK caches `access_token` in memory and refreshes it when it is close to expiry.

### OAuth env vars (fallback mode)

Set these in the notebook runtime before use:

- `OQULLUS_OAUTH_TOKEN_URL`
- `OQULLUS_OAUTH_CLIENT_ID`
- `OQULLUS_OAUTH_CLIENT_SECRET`
- `OQULLUS_OAUTH_GRANT_TYPE` (`refresh_token` or `client_credentials`)

If `OQULLUS_OAUTH_GRANT_TYPE=refresh_token` (default):

- `OQULLUS_OAUTH_ACCESS_TOKEN`
- `OQULLUS_OAUTH_REFRESH_TOKEN`

If `OQULLUS_OAUTH_GRANT_TYPE=client_credentials`:

- `OQULLUS_OAUTH_SCOPE` (optional)
- `OQULLUS_OAUTH_AUDIENCE` (optional)

## Integration test (client credentials)

Install test deps:

```bash
pip install -e ".[dev]"
```

Set:

- `WORKSPACE_API_BASE_URL` (workspace API base URL)
- `OQULLUS_OAUTH_GRANT_TYPE=client_credentials`
- `OQULLUS_OAUTH_TOKEN_URL` (OAuth token endpoint)
- `OQULLUS_OAUTH_CLIENT_ID`
- `OQULLUS_OAUTH_CLIENT_SECRET`
- `OQULLUS_OAUTH_SCOPE` (optional)
- `OQULLUS_OAUTH_AUDIENCE` (optional)

The integration test currently hardcodes workspace path and expected text in
`tests/integration/test_client_credentials.py`.

Run:

```bash
pytest -m integration tests/integration/test_client_credentials.py
```
