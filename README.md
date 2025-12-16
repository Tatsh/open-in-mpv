# open-in-mpv

[![Python versions](https://img.shields.io/pypi/pyversions/open-in-mpv.svg?color=blue&logo=python&logoColor=white)](https://www.python.org/)
[![PyPI - Version](https://img.shields.io/pypi/v/open-in-mpv)](https://pypi.org/project/open-in-mpv/)
[![GitHub tag (with filter)](https://img.shields.io/github/v/tag/Tatsh/open-in-mpv)](https://github.com/Tatsh/open-in-mpv/tags)
[![License](https://img.shields.io/github/license/Tatsh/open-in-mpv)](https://github.com/Tatsh/open-in-mpv/blob/master/LICENSE.txt)
[![GitHub commits since latest release (by SemVer including pre-releases)](https://img.shields.io/github/commits-since/Tatsh/open-in-mpv/v0.1.3/master)](https://github.com/Tatsh/open-in-mpv/compare/v0.1.3...master)
[![CodeQL](https://github.com/Tatsh/open-in-mpv/actions/workflows/codeql.yml/badge.svg)](https://github.com/Tatsh/open-in-mpv/actions/workflows/codeql.yml)
[![QA](https://github.com/Tatsh/open-in-mpv/actions/workflows/qa.yml/badge.svg)](https://github.com/Tatsh/open-in-mpv/actions/workflows/qa.yml)
[![Tests](https://github.com/Tatsh/open-in-mpv/actions/workflows/tests.yml/badge.svg)](https://github.com/Tatsh/open-in-mpv/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/Tatsh/open-in-mpv/badge.svg?branch=master)](https://coveralls.io/github/Tatsh/open-in-mpv?branch=master)
[![Dependabot](https://img.shields.io/badge/Dependabot-enabled-blue?logo=dependabot)](https://github.com/dependabot)
[![Documentation Status](https://readthedocs.org/projects/open-in-mpv/badge/?version=latest)](https://open-in-mpv.readthedocs.org/?badge=latest)
[![mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
[![Poetry](https://img.shields.io/badge/Poetry-242d3e?logo=poetry)](https://python-poetry.org)
[![pydocstyle](https://img.shields.io/badge/pydocstyle-enabled-AD4CD3?logo=pydocstyle)](https://www.pydocstyle.org/)
[![pytest](https://img.shields.io/badge/pytest-enabled-CFB97D?logo=pytest)](https://docs.pytest.org)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Downloads](https://static.pepy.tech/badge/open-in-mpv/month)](https://pepy.tech/project/open-in-mpv)
[![Stargazers](https://img.shields.io/github/stars/Tatsh/open-in-mpv?logo=github&style=flat)](https://github.com/Tatsh/open-in-mpv/stargazers)
[![Prettier](https://img.shields.io/badge/Prettier-enabled-black?logo=prettier)](https://prettier.io/)

[![@Tatsh](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fpublic.api.bsky.app%2Fxrpc%2Fapp.bsky.actor.getProfile%2F%3Factor=did%3Aplc%3Auq42idtvuccnmtl57nsucz72&query=%24.followersCount&style=social&logo=bluesky&label=Follow+%40Tatsh)](https://bsky.app/profile/Tatsh.bsky.social)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Tatsh-black?logo=buymeacoffee)](https://buymeacoffee.com/Tatsh)
[![Libera.Chat](https://img.shields.io/badge/Libera.Chat-Tatsh-black?logo=liberadotchat)](irc://irc.libera.chat/Tatsh)
[![Mastodon Follow](https://img.shields.io/mastodon/follow/109370961877277568?domain=hostux.social&style=social)](https://hostux.social/@Tatsh)
[![Patreon](https://img.shields.io/badge/Patreon-Tatsh2-F96854?logo=patreon)](https://www.patreon.com/Tatsh2)

![Context menu item](https://raw.githubusercontent.com/Tatsh/open-in-mpv/master/context-item.png)

This browser extension displays a context menu item _Open in mpv_ for links. When clicked it will
pass the URL of the link to mpv (which must be `PATH`).

If you have yt-dlp installed and in `PATH`, then mpv will try to use it to resolve URLs it cannot
handle. This means you can right-click on any YouTube video page or link, choose `Open in mpv` and
view the video with mpv.

## Installation

First, [install the extension](https://github.com/Tatsh/open-in-mpv/releases). Quit your browser.

There are many ways to perform the next step. Below is the most basic, assuming you have Pip
installed.

Gentoo users can simply install `media-video/open-in-mpv` from
[my overlay](https://github.com/Tatsh/tatsh-overlay).

```shell
pip install --user open-in-mpv
open-in-mpv-install --user --force
```

The above commands will install the native host JSON file to supported Chromium-based browsers
whose paths are known for your OS. `--force` is used on first install to create the necessary paths
if they do not exist.

See `open-in-mpv-install --help` for more options. Linux users can pass the `--system` option to
install the native host part of the extension system-wide.

## Uninstallation

```shell
open-in-mpv-uninstall
pip remove --user open-in-mpv
```

Uninstall the extension from your browser.

## Known issues

**Linux**: mpv is launched with `--gpu-api=opengl` because with Vulkan it starts but fails to open a
window.

At this time, Windows is not supported by the `open-in-mpv` Python script. It may work, but it is
not supported.
