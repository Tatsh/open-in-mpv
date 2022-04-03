# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.0.5   | :white_check_mark: |

## Reporting a Vulnerability

Report a vulnerability to the project's
[GitHub issues](https://github.com/Tatsh/open-in-mpv/issues), unless the
vulnerability is considered critical. In that case, email me.

### Potential issues that are _not_ considered vulnerabilities

- In the `open-in-mpv` Python script: running a rogue `mpv` executable (where
  it is likely a user has a compromised system).
- `install.ps1` may require extra permissions on the user's part. The user is
  responsible for managing their system's security policies.
- Anything in the `test-open` script as this is only for testing for use by
  developers.
- The lack of a complete uninstaller.
