# Windows Installation and Development Guide

## Installation

### Using the Installer (Recommended)

1. Download the latest `open-in-mpv-installer.exe` from the
   [releases page](https://github.com/Tatsh/open-in-mpv/releases)
2. Run the installer
3. The installer will:
   - Install the native messaging host
   - Download and install mpv
   - Configure native messaging for all detected browsers (Chrome, Firefox, Opera, etc.)
4. Install the browser extension from the Chrome Web Store or load it manually

### Manual Installation

If you prefer to install manually:

1. Install Python 3.10 or later
2. Install the package:

   ```powershell
   pip install --user open-in-mpv
   ```

3. Install mpv from [mpv.io](https://mpv.io/) and add it to your PATH
4. Install the native messaging host manually (see Python code in `open_in_mpv/install.py`)

## Building the Installer

### Prerequisites

- Python 3.10 or later
- Poetry
- NSIS (Nullsoft Scriptable Install System)
- 7-Zip (for extracting mpv)

### Build Steps

1. Clone the repository:

   ```powershell
   git clone https://github.com/Tatsh/open-in-mpv.git
   cd open-in-mpv
   ```

2. Install dependencies:

   ```powershell
   poetry install
   poetry run pip install pyinstaller
   ```

3. Build the executable with PyInstaller:

   ```powershell
   poetry run pyinstaller open-in-mpv.spec
   ```

4. Download mpv:

   ```powershell
   # Download and extract mpv-x86_64-latest.7z from SourceForge
   # Copy mpv.exe to the dist/ folder
   ```

5. Build the installer with NSIS:

   ```powershell
   makensis installer.nsi
   ```

6. The installer will be created as `open-in-mpv-installer.exe`

## Development Notes

### PyInstaller Bundle Detection

The application detects if it's running from a PyInstaller bundle using `sys.frozen`. When running
from a bundle on Windows, it will automatically use the bundled `mpv.exe` from the same directory.

### Native Messaging Host Configuration

On Windows, the native messaging host JSON files are installed to:

- Chrome: `%LOCALAPPDATA%\Google\Chrome\NativeMessagingHosts`
- Chrome Beta: `%LOCALAPPDATA%\Google\Chrome Beta\NativeMessagingHosts`
- Chrome Canary: `%LOCALAPPDATA%\Google\Chrome SxS\NativeMessagingHosts`
- Chromium: `%LOCALAPPDATA%\Chromium\NativeMessagingHosts`
- Firefox: `%APPDATA%\Mozilla\NativeMessagingHosts`
- Opera: `%APPDATA%\Opera Software\NativeMessagingHosts`

The installer will detect which browsers are installed and create the configuration files only for
those browsers.

## Troubleshooting

### mpv.exe not found

If you see errors about mpv.exe not being found:

1. Check that mpv.exe is in the same directory as open-in-mpv.exe
2. Or ensure mpv is installed and in your PATH

### Extension cannot connect to native host

1. Check that the native messaging host JSON files exist in the correct locations
2. Verify the path in the JSON file points to the correct location of open-in-mpv.exe
3. Restart your browser completely (close all windows)

### Permission errors

The installer runs as a normal user and installs to `%LOCALAPPDATA%\open-in-mpv`. If you
encounter permission errors, ensure this directory is writable by your user account.
