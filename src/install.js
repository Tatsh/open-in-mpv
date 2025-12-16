// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2020 Andrew Udvare

/**
 * Detect the user's platform and show appropriate installation instructions.
 */
function detectPlatform() {
  const platform = navigator.platform.toLowerCase();
  const userAgent = navigator.userAgent.toLowerCase();

  let detectedPlatform = 'linux';

  if (platform.includes('win') || userAgent.includes('windows')) {
    detectedPlatform = 'windows';
  } else if (platform.includes('mac') || userAgent.includes('mac')) {
    detectedPlatform = 'mac';
  }

  const platformDiv = document.getElementById(`${detectedPlatform}-instructions`);
  if (platformDiv) {
    platformDiv.classList.add('active');
  }

  // Set up download link for Windows
  if (detectedPlatform === 'windows') {
    const downloadLink = document.getElementById('windows-download');
    if (downloadLink) {
      downloadLink.href =
        'https://github.com/Tatsh/open-in-mpv/releases/latest/download/open-in-mpv-installer.exe';
    }
  }
}

// Run on page load
document.addEventListener('DOMContentLoaded', detectPlatform);
