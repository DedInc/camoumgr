# CamouMgr

**CamouMgr** is a modern, premium profile manager for [Camoufox](https://github.com/daijro/camoufox), built with Python and CustomTkinter. It allows you to easily manage and launch multiple browser profiles with distinct configurations (proxies, OS fingerprints) in a sleek, dark-themed GUI.

## Features

- **Profile Management**: Create, delete, and organize multiple browser profiles effortlessly.
- **Custom Configurations**: 
  - **Proxies**: Support for HTTP/HTTPS/SOCKS proxies with authentication.
  - **OS Fingerprinting**: Spoof different operating systems (Windows, MacOS, Linux) per profile.
- **Persistent Sessions**: Browser state (cookies, local storage) is automatically saved and restored for each profile, ensuring continuity.
- **Modern UI**: A polished, dark-themed interface featuring:
  - Responsive layout
  - Visual feedback and hover effects
  - Activity logging
  - Pagination for profile lists
- **Privacy Focused**: leverages Camoufox's anti-detect capabilities to protect your identity.

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
   pip install customtkinter camoufox
   ```

## Usage

1. **Start the Application**
   Run the main script from the project root:
   ```bash
   python src/main.py
   ```

2. **Creating a Profile**
   - Click the **"Add Profile"** button in the sidebar.
   - Enter a unique **Profile Name**.
   - (Optional) Enter a **Proxy** string. Supported formats:
     - `http://user:pass@host:port`
     - `host:port` (assumes http)
   - Select a target **Operating System** from the dropdown.
   - Click **"Create"**.

3. **Launching a Profile**
   - Find the profile card in the main view.
   - Click the **"Launch"** button (rocket icon).
   - The Camoufox browser will open with the configured settings.
   - **Note**: You can close the browser manually or click the **"CLOSE"** button (red) on the profile card to gracefully shut it down.

4. **Editing a Profile**
   - Click the **Edit** button (pencil icon) on a profile card.
   - You can modify the profile name, proxy, and OS type.
   - Click **"Save Changes"** to apply.

5. **Managing Profiles**
   - Use the **Delete** button (trash icon) on a profile card to remove it and its associated data.
   - Use the pagination controls at the bottom if you have many profiles.

## Configuration

You can customize the application theme and other settings in `src/config.py`. The application uses a "Premium Dark" color palette by default.

## License

[MIT License](LICENSE)
