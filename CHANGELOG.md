# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Windows installer for easy setup of the native messaging host (sets up Chrome, Chrome Beta,
  Chrome Canary, Chromium, Firefox, and Opera if they are installed).
  - Also bundles a copy of `mpv` and `yt-dlp`.
- macOS installer (pkg file).
- Post-installation page for browser extension with platform-specific instructions.
- Post-uninstallation page for browser extension.

### Changed

- Removed Linux-specific `--gpu-api=opengl` flag on Windows.

## [0.1.3]

### Fixed

- Logging.

[unreleased]: https://github.com/Tatsh/open-in-mpv/compare/v0.1.3...HEAD
[0.1.3]: https://github.com/Tatsh/open-in-mpv/compare/v0.1.2...v0.1.3
