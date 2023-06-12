# Open in mpv

[![QA](https://github.com/Tatsh/open-in-mpv/workflows/QA/badge.svg)](https://github.com/Tatsh/open-in-mpv/actions?query=workflow%3AQA)
[![Lint Python](https://github.com/Tatsh/open-in-mpv/workflows/Lint%20python/badge.svg)](https://github.com/Tatsh/open-in-mpv/actions?query=workflow%3A%22Lint+python%22)

![Context menu item](context-item.png)

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
