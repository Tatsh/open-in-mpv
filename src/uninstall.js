// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2020 Andrew Udvare

// Detect the user's platform and show appropriate uninstallation instructions.
document.addEventListener('DOMContentLoaded', () => {
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
});
