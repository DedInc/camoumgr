<div align="center">
  <img src="src/assets/icon.png" width="128" alt="CamouMgr logo" />
</div>

# CamouMgr

CamouMgr is a GUI profile manager for [Camoufox](https://github.com/daijro/camoufox), written in Python using the Flet framework. It provides a straightforward way to configure and run multiple isolated browser sessions, each with its own proxy and OS fingerprint.

## Features

- Isolated browser state (cookies, local storage) per profile.
- Proxy configuration (HTTP/HTTPS/SOCKS5) with basic auth support and a built-in connectivity checker.
- Basic OS fingerprint spoofing (Windows, macOS, Linux).
- Export and import profiles as ZIP archives (includes browser data).
- Thread-safe browser launching to avoid session overlap issues.

## Setup

Requires Python 3.8 or newer. Setting it up in a virtual environment is recommended to avoid dependency conflicts.

```bash
git clone https://github.com/DedInc/camoumgr.git
cd camoumgr

python -m venv venv

# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

## Usage

Start the UI by running:

```bash
python src/main.py
```

From the interface, you can add new profiles, assign proxies, and launch the browser instances. Closing the browser instance from the UI or the browser itself will automatically save the session state to disk.

Supported proxy formats:
- `http://user:pass@host:port`
- `socks5://user:pass@host:port`
- `host:port` (defaults to http)

*Note: The live proxy check might hang for a few seconds if the provided proxy is completely dead or dropping packets. You can adjust the timeout limit in the `.env` file.*

## Configuration

The application relies on a `.env` file for local path and behavior configuration. Copy `.env.example` to `.env` in the root directory if you need to override the defaults:

| Variable | Default | Description |
|---|---|---|
| `CAMOUMGR_PROFILES_FILE` | `profiles.json` | Where profile metadata is stored. |
| `CAMOUMGR_DATA_DIR` | `camoufox_data` | Directory where the actual browser profile data is written. |
| `CAMOUMGR_LOG_DIR` | `logs` | Directory for daily log files. |
| `CAMOUMGR_LOG_LEVEL` | `INFO` | Python log level (DEBUG, INFO, WARNING, ERROR). |
| `CAMOUMGR_PROXY_TIMEOUT` | `10` | Timeout in seconds for the proxy checker. |

## License

MIT License