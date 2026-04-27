# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.1/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.1] - 2026-04-27

### Added

- Packed Chrome extension (`.crx`) is now built and attached to GitHub releases.

### Fixed

- Restored Windows installer (NSIS) and macOS package (pkg) attachments on GitHub releases. Both
  were absent from v0.2.0 due to a CI regression that left their reusable workflows without a
  caller.

## [0.2.0] - 2026-04-27

### Added

- Windows installer for easy setup of the native messaging host (sets up Chrome, Chrome Beta,
  Chrome Canary, Chromium, Firefox, and Opera if they are installed).
  - Also bundles a copy of `mpv` and `yt-dlp`.
- macOS installer (pkg file).
- Post-installation page for browser extension with platform-specific instructions.
- Post-uninstallation page for browser extension.

### Changed

- Removed Linux-specific `--gpu-api=opengl` flag on Windows.

### Fixed

- `main` command help text now describes the native-messaging wire format correctly (4-byte length
  prefix plus JSON).

## [0.1.3]

### Fixed

- Logging.

[unreleased]: https://github.com/Tatsh/open-in-mpv/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/Tatsh/open-in-mpv/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/Tatsh/open-in-mpv/compare/v0.1.3...v0.2.0
[0.1.3]: https://github.com/Tatsh/open-in-mpv/compare/v0.1.2...v0.1.3
