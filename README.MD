<div align="center">
  <img src="src/assets/icon.png" width="128" alt="CamouMgr logo" />
</div>

# CamouMgr

CamouMgr is a desktop manager for [Camoufox](https://github.com/daijro/camoufox) profiles. It gives you a local UI for creating browser profiles, assigning proxies, choosing an OS fingerprint, launching sessions, and moving profiles in and out of ZIP archives.

The app also starts a small local REST API next to the GUI, so the same profile operations can be scripted.

## What is in the app

- Create, edit, rename, and delete profiles.
- Assign a proxy per profile.
- Choose an OS type per profile: `windows`, `linux`, or `macos`.
- Launch and stop browser sessions from the GUI.
- Select multiple profiles and run bulk launch, stop, or delete actions.
- Check proxy connectivity from the profile dialog.
- Export profiles to ZIP archives, with or without browser data.
- Import profiles from ZIP archives, with optional overwrite behavior.
- View recent activity in the sidebar log and open a larger log window.
- Page through the profile list when you have more than 10 profiles.
- Use the built-in local API for automation.

## Requirements

- Python 3.10 or newer
- A working Python environment that can install the packages in `requirements.txt`

The repository includes `run_cmngr.bat` for Windows. The Python entry point works directly as well.

## Installation

```bash
git clone https://github.com/DedInc/camoumgr.git
cd camoumgr

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

## Running the app

Start the GUI and local API together:

```bash
python -m src.main
```

On Windows you can also use:

```bat
run_cmngr.bat
```

When the app starts, it launches:

- the Flet desktop UI
- the FastAPI server on `http://127.0.0.1:8000` by default

Swagger UI is available at `http://127.0.0.1:8000/docs` and ReDoc at `http://127.0.0.1:8000/redoc`.

## Configuration

All configuration is optional. If you want to override defaults, copy `.env.example` to `.env` in the project root.

| Variable | Default | Description |
| --- | --- | --- |
| `CAMOUMGR_PROFILES_FILE` | `profiles.json` | JSON file used to store profile metadata. |
| `CAMOUMGR_DATA_DIR` | `camoufox_data` | Directory that stores per-profile browser data. |
| `CAMOUMGR_LOG_DIR` | `logs` | Directory for daily log files. |
| `CAMOUMGR_LOG_LEVEL` | `INFO` | Python log level. |
| `CAMOUMGR_PROXY_TIMEOUT` | `10` | Default timeout, in seconds, for proxy checks. |
| `CAMOUMGR_API_HOST` | `127.0.0.1` | Host used by the local API server. |
| `CAMOUMGR_API_PORT` | `8000` | Port used by the local API server. |

## Storage layout

By default, the project writes data to these locations:

- `profiles.json` - profile metadata
- `camoufox_data\<profile-name>\` - browser data for each profile
- `logs\camoumgr_YYYYMMDD.log` - daily log file

Exported ZIP files contain:

- `profile.json`
- `data\...` when export is run with browser data included

## Proxy format

Accepted proxy formats:

- `host:port`
- `http://host:port`
- `https://host:port`
- `socks4://host:port`
- `socks5://host:port`
- `http://user:pass@host:port`
- `socks5://user:pass@host:port`

Rules enforced by the validator:

- scheme is optional
- supported schemes are `http`, `https`, `socks4`, and `socks5`
- port must be in the range `1-65535`
- an empty proxy value is allowed

The GUI proxy checker uses the configured timeout and reports either the detected IP or the failure message.

## Profile name rules

Profile names are validated before they are saved.

- must not be empty
- must be 64 characters or fewer
- must not start or end with spaces
- must not contain `< > : " / \ | ? *`
- must not be a reserved Windows name such as `CON`, `PRN`, `AUX`, `NUL`, `COM1`-`COM9`, or `LPT1`-`LPT9`

## Local API reference

The API is intended for local automation. There is no authentication layer in the code, so leaving it bound to localhost is the safe default.

Base prefix:

```text
/api/v1
```

### Health

| Method | Path | Notes |
| --- | --- | --- |
| `GET` | `/health` | Returns a basic success message. |

Example response:

```json
{
  "success": true,
  "message": "CamouMgr API is running"
}
```

### Profiles

| Method | Path | Notes |
| --- | --- | --- |
| `GET` | `/profiles` | List all profiles. |
| `POST` | `/profiles` | Create a profile. |
| `GET` | `/profiles/{name}` | Get one profile, including `data_dir` and `is_running`. |
| `PATCH` | `/profiles/{name}` | Update only the supplied fields. |
| `DELETE` | `/profiles/{name}` | Delete a profile and its data directory. |
| `GET` | `/profiles/{name}/data-dir` | Return the resolved data directory and whether it exists. |
| `POST` | `/profiles/{name}/export` | Export one profile to a ZIP file. |
| `POST` | `/profiles/import` | Import one profile from a ZIP file. |

Create profile request:

```json
{
  "name": "my-profile",
  "proxy": "socks5://user:pass@127.0.0.1:1080",
  "os_type": "linux"
}
```

Create and update fields:

- `name`: string
- `proxy`: string or `null`
- `os_type`: string, default `windows`

Update uses the same fields, but all of them are optional.

Profile response shape:

```json
{
  "name": "my-profile",
  "proxy": "socks5://user:pass@127.0.0.1:1080",
  "os_type": "linux",
  "data_dir": "C:\\path\\to\\camoufox_data\\my-profile",
  "is_running": false
}
```

Export request:

```json
{
  "export_dir": "C:\\Exports",
  "include_data": true
}
```

Export response:

```json
{
  "success": true,
  "zip_path": "C:\\Exports\\my-profile_20260313_134500.zip",
  "error": null
}
```

Import request:

```json
{
  "zip_path": "C:\\Exports\\my-profile_20260313_134500.zip",
  "overwrite": false
}
```

Import response:

```json
{
  "success": true,
  "profile_name": "my-profile",
  "error": null
}
```

Profile endpoint behavior worth knowing:

- `POST /profiles` returns `201 Created`
- `PATCH /profiles/{name}` can return `409` when a rename conflicts, or when the browser for that profile is running and the name change is blocked
- `DELETE /profiles/{name}` returns `409` if the browser is still running
- `POST /profiles/{name}/export` requires `export_dir` to already exist
- `POST /profiles/import` requires `profile.json` inside the ZIP archive

### Browser

| Method | Path | Notes |
| --- | --- | --- |
| `GET` | `/browser` | List names of running browser sessions. |
| `GET` | `/browser/{name}/status` | Return running status for one profile. |
| `POST` | `/browser/{name}/launch` | Start a browser session asynchronously. |
| `POST` | `/browser/{name}/stop` | Stop a running browser session. |

Running browser response:

```json
{
  "running": ["profile-a", "profile-b"],
  "count": 2
}
```

Launch response:

```json
{
  "success": true,
  "message": "Browser launching for 'my-profile'"
}
```

Browser endpoint behavior worth knowing:

- `POST /browser/{name}/launch` returns `202 Accepted`
- launch is asynchronous; use `GET /browser/{name}/status` or `GET /browser` to check state
- `POST /browser/{name}/launch` returns `409` if the profile is already running
- `POST /browser/{name}/stop` returns `409` if the profile is not running

### Proxy

| Method | Path | Notes |
| --- | --- | --- |
| `POST` | `/proxy/check` | Validate and test a proxy. |

Request:

```json
{
  "proxy": "socks5://user:pass@127.0.0.1:1080",
  "timeout": 10
}
```

Response:

```json
{
  "success": true,
  "message": "203.0.113.10"
}
```

## Quick API examples

Create a profile:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/profiles ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"work\",\"proxy\":\"socks5://user:pass@127.0.0.1:1080\",\"os_type\":\"linux\"}"
```

Get the resolved data directory:

```bash
curl http://127.0.0.1:8000/api/v1/profiles/work/data-dir
```

Launch a browser:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/browser/work/launch
```

Check whether it is running:

```bash
curl http://127.0.0.1:8000/api/v1/browser/work/status
```

Check a proxy:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/proxy/check ^
  -H "Content-Type: application/json" ^
  -d "{\"proxy\":\"socks5://user:pass@127.0.0.1:1080\",\"timeout\":10}"
```

## Project layout

```text
src\
  api\         FastAPI app, routes, and schemas
  core\        config, container, logging, events
  interfaces\  service protocols
  models\      profile model
  services\    profile, browser, and proxy services
  ui\          Flet UI, dialogs, and actions
  utils\       validation and helper utilities
```

## License

MIT License
