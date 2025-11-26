# CamouMgr

**CamouMgr** is a modern, premium profile manager for [Camoufox](https://github.com/daijro/camoufox), built with Python and CustomTkinter. It allows you to easily manage and launch multiple browser profiles with distinct configurations (proxies, OS fingerprints) in a sleek, dark-themed GUI.

## Features

- **Profile Management**: Create, edit, delete, and organize multiple browser profiles effortlessly.
- **Custom Configurations**: 
  - **Proxies**: Support for HTTP/HTTPS/SOCKS proxies with authentication.
  - **OS Fingerprinting**: Spoof different operating systems (Windows, MacOS, Linux) per profile.
- **Persistent Sessions**: Browser state (cookies, local storage) is automatically saved and restored for each profile, ensuring continuity.
- **Profile Export/Import**: Backup and transfer profiles between machines as ZIP archives, including browser data.
- **Proxy Validation**: 
  - Format validation before saving.
  - Live proxy connectivity check with real IP verification.
- **Input Validation**: Profile names are validated for filesystem compatibility with clear error messages.
- **Environment Configuration**: Customize paths and settings via `.env` file without modifying code.
- **File Logging**: All activity is logged to daily log files in the `logs/` directory.
- **Localization Ready**: All UI strings are centralized for easy translation.
- **Thread-Safe Operations**: Browser sessions are managed with proper locking to prevent race conditions.
- **Modern UI**: A polished, dark-themed interface featuring:
  - Responsive layout
  - Visual feedback and hover effects
  - Activity logging with expandable view
  - Pagination for profile lists
- **Privacy Focused**: Leverages Camoufox's anti-detect capabilities to protect your identity.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/DedInc/camoumgr/
   cd camoumgr
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env to customize settings
   ```

## Usage

1. **Start the Application**
   Run the main script from the project root:
   ```bash
   python src/main.py
   ```

2. **Creating a Profile**
   - Click the **"+ NEW PROFILE"** button in the sidebar.
   - Enter a unique **Profile Name**.
   - (Optional) Enter a **Proxy** string. Supported formats:
     - `http://user:pass@host:port`
     - `socks5://user:pass@host:port`
     - `host:port` (assumes http)
   - (Optional) Click **"Check Proxy"** to verify connectivity.
   - Select a target **Operating System** from the dropdown.
   - Click **"Create Profile"**.

3. **Launching a Profile**
   - Find the profile card in the main view.
   - Click the **"LAUNCH"** button.
   - The Camoufox browser will open with the configured settings.
   - Click the **"CLOSE"** button (red) on the profile card to shut it down.

4. **Editing a Profile**
   - Click the **Edit** button (✎) on a profile card.
   - Modify the profile name, proxy, or OS type.
   - Click **"Save Changes"** to apply.

5. **Export/Import Profiles**
   - **Export**: Click "Export Profile" in the sidebar, select a profile, choose whether to include browser data, and select a destination folder.
   - **Import**: Click "Import Profile" in the sidebar and select a `.zip` archive.

6. **Managing Profiles**
   - Use the **Delete** button (×) on a profile card to remove it and its associated data.
   - Use the pagination controls at the bottom if you have many profiles.

## Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`) to customize:

| Variable | Default | Description |
|----------|---------|-------------|
| `CAMOUMGR_PROFILES_FILE` | `profiles.json` | Profile storage file |
| `CAMOUMGR_DATA_DIR` | `camoufox_data` | Browser data directory |
| `CAMOUMGR_LOG_DIR` | `logs` | Log files directory |
| `CAMOUMGR_LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `CAMOUMGR_PROXY_TIMEOUT` | `10` | Proxy check timeout in seconds |

### Theme Customization

You can customize the application theme colors in `src/config.py`. The application uses a "Premium Dark" color palette by default.

## License

[MIT License](LICENSE)
