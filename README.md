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

- `OAUTH_TOKEN_URL`
- `OAUTH_CLIENT_ID`
- `OAUTH_CLIENT_SECRET`
- `OAUTH_GRANT_TYPE` (`refresh_token` or `client_credentials`)

If `OAUTH_GRANT_TYPE=refresh_token` (default):

- `OAUTH_ACCESS_TOKEN`
- `OAUTH_REFRESH_TOKEN`

If `OAUTH_GRANT_TYPE=client_credentials`:

- `OAUTH_SCOPE` (optional)
- `OAUTH_AUDIENCE` (optional)

## Integration test (client credentials)

Install test deps:

```bash
pip install -e ".[dev]"
```

Set:

- `WORKSPACE_API_BASE_URL` (workspace API base URL)
- `OQULLUS_INTEGRATION_TOKEN_URL` (OAuth token endpoint)
- `OQULLUS_INTEGRATION_CLIENT_ID`
- `OQULLUS_INTEGRATION_CLIENT_SECRET`

The integration test currently hardcodes workspace path and expected text in
`tests/integration/test_client_credentials.py`.

Run:

```bash
pytest -m integration tests/integration/test_client_credentials.py
```
