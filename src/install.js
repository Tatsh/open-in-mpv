/**
 * This file is part of open-in-mpv.
 *
 * Copyright 2020 Andrew Udvare
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to
 * deal in the Software without restriction, including without limitation the
 * rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 * sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
 */

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
      // This URL should be updated to point to the actual release
      downloadLink.href =
        'https://github.com/Tatsh/open-in-mpv/releases/latest/download/open-in-mpv-installer.exe';
    }
  }
}

// Run on page load
document.addEventListener('DOMContentLoaded', detectPlatform);
