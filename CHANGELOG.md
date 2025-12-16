# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Windows NSIS installer for automated setup.
- Automatic mpv download and installation on Windows (version 20251214-git-f7be2ee).
- Automatic yt-dlp download and installation on Windows (version 2025.12.08).
- Native messaging host installation for Chrome, Chrome Beta, Chrome Canary, Chromium, Firefox, and Opera.
- Post-installation page for browser extension with platform-specific instructions.
- Post-uninstallation reminder page for browser extension.
- Windows PyInstaller bundle detection for using bundled mpv.exe and yt-dlp.exe.
- Automatic yt-dlp integration when available on Windows.

### Changed

- Removed Linux-specific `--gpu-api=opengl` flag on Windows.
- Updated JavaScript files to use SPDX license identifiers.

## [0.1.3]

### Fixed

- Logging.

[unreleased]: https://github.com/Tatsh/open-in-mpv/compare/v0.1.3...HEAD
[0.1.3]: https://github.com/Tatsh/open-in-mpv/compare/v0.1.2...v0.1.3
