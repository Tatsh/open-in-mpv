# open-in-mpv

[![Python versions](https://img.shields.io/pypi/pyversions/open-in-mpv.svg?color=blue&logo=python&logoColor=white)](https://www.python.org/)
[![PyPI - Version](https://img.shields.io/pypi/v/open-in-mpv)](https://pypi.org/project/open-in-mpv/)
[![GitHub tag (with filter)](https://img.shields.io/github/v/tag/Tatsh/open-in-mpv)](https://github.com/Tatsh/open-in-mpv/tags)
[![License](https://img.shields.io/github/license/Tatsh/open-in-mpv)](https://github.com/Tatsh/open-in-mpv/blob/master/LICENSE.txt)
[![GitHub commits since latest release (by SemVer including pre-releases)](https://img.shields.io/github/commits-since/Tatsh/open-in-mpv/v0.1.2/master)](https://github.com/Tatsh/open-in-mpv/compare/v0.1.2...master)
[![QA](https://github.com/Tatsh/open-in-mpv/actions/workflows/qa.yml/badge.svg)](https://github.com/Tatsh/open-in-mpv/actions/workflows/qa.yml)
[![Tests](https://github.com/Tatsh/open-in-mpv/actions/workflows/tests.yml/badge.svg)](https://github.com/Tatsh/open-in-mpv/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/Tatsh/open-in-mpv/badge.svg?branch=master)](https://coveralls.io/github/Tatsh/open-in-mpv?branch=master)
[![Documentation Status](https://readthedocs.org/projects/open-in-mpv/badge/?version=latest)](https://open-in-mpv.readthedocs.org/?badge=latest)
[![mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![pydocstyle](https://img.shields.io/badge/pydocstyle-enabled-AD4CD3)](http://www.pydocstyle.org/en/stable/)
[![pytest](https://img.shields.io/badge/pytest-zz?logo=Pytest&labelColor=black&color=black)](https://docs.pytest.org/en/stable/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Downloads](https://static.pepy.tech/badge/open-in-mpv/month)](https://pepy.tech/project/open-in-mpv)
[![Stargazers](https://img.shields.io/github/stars/Tatsh/open-in-mpv?logo=github&style=flat)](https://github.com/Tatsh/open-in-mpv/stargazers)

[![@Tatsh](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fpublic.api.bsky.app%2Fxrpc%2Fapp.bsky.actor.getProfile%2F%3Factor%3Ddid%3Aplc%3Auq42idtvuccnmtl57nsucz72%26query%3D%24.followersCount%26style%3Dsocial%26logo%3Dbluesky%26label%3DFollow%2520%40Tatsh&query=%24.followersCount&style=social&logo=bluesky&label=Follow%20%40Tatsh)](https://bsky.app/profile/Tatsh.bsky.social)
[![Mastodon Follow](https://img.shields.io/mastodon/follow/109370961877277568?domain=hostux.social&style=social)](https://hostux.social/@Tatsh)

![Context menu item](https://raw.githubusercontent.com/Tatsh/open-in-mpv/master/context-item.png)

This browser extension displays a context menu item _Open in mpv_ for links. When clicked it will
pass the URL of the link to mpv (which must be `PATH`).

If you have yt-dlp installed and in `PATH`, then mpv will try to use it to resolve URLs it cannot
handle. This means you can right-click on any YouTube video page or link, choose `Open in mpv` and
view the video with mpv.

## Installation

First, [install the extension](https://chrome.google.com/webstore/detail/open-in-mpv/ggijpepdpiehgbiknmfpfbhcalffjlbj/).
Quit your browser.

There are many ways to perform the next step. Below is the most basic, assuming you have Pip
installed. Before running the commands below, quit your browser.

Gentoo users can simply install `media-video/open-in-mpv` from
[my overlay](https://github.com/Tatsh/tatsh-overlay).

```shell
pip install --user open-in-mpv
open-in-mpv-install --user
```

The above will install the native host JSON file to supported Chromium-based browsers whose paths are
known, but only if the browser has created the directories before. If you want to force the
installation you can pass `--force`.

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
