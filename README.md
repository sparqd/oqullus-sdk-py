# oqullus-sdk-py

Minimal SDK for fetching workspace files in a Jupyter runtime.

## Usage

```python
from oqullus_sdk import OqullusClient

client = OqullusClient()

local_path = client.workspace.fetch_file(
    "my_workspace@example.com/data.csv"
)
print(f"File written to: {local_path}")
```

### Refresh token env vars

Set these in the notebook runtime before use:

- `OAUTH_ACCESS_TOKEN`
- `OAUTH_REFRESH_TOKEN`
- `OAUTH_TOKEN_URL`
- `OAUTH_CLIENT_ID`
- `OAUTH_CLIENT_SECRET`
