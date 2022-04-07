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
 * @typedef InitResponse
 * @property {string} logPath
 * @property {string} socketPath
 * @property {string} version
 */

/** @type ParentNode['querySelector'] */
const qs = document.querySelector.bind(document);
/** @type HTMLButtonElement */
const button = qs('#save');
/** @type HTMLFormElement */
const form = qs('form');
/** @type {{[x: string]: HTMLInputElement}} */
const checkboxFields = {
  debugFlag: qs('#debug'),
  singleFlag: qs('#single'),
};
const defaults = {
  debugFlag: false,
  singleFlag: true,
};
/** @type HTMLElement */
const logFile = qs('#log-file');
/** @type HTMLSpanElement */
const saved = qs('#saved');
/** @type HTMLElement */
const socket = qs('#socket');
/** @type HTMLElement */
const version = qs('#version');
const WAIT_TIME = 5000;
form.addEventListener('submit', event => {
  event.preventDefault();
  const data = {};
  for (const key of Object.keys(checkboxFields)) {
    data[key] = checkboxFields[key].checked;
  }
  button.disabled = true;
  chrome.storage.local.set(data, () => {
    button.disabled = false;
    saved.classList.remove('d-none');
    setTimeout(() => saved.classList.add('d-none'), WAIT_TIME);
  });
  return false;
});
document.querySelectorAll('.fw-bold').forEach(el => {
  el.addEventListener('mousedown', async () => {
    const result = await navigator.permissions.query({
      name: /** @type PermissionName */ 'clipboard-write',
    });
    if (result.state === 'granted' || result.state === 'prompt') {
      try {
        await navigator.clipboard.writeText(
          el.querySelector('.font-monospace').innerText.trim()
        );
        /** @type HTMLSpanElement */
        const copied = el.querySelector('.copied');
        copied.classList.remove('d-none');
        setTimeout(() => copied.classList.add('d-none'), WAIT_TIME);
      } catch (e) {
        console.error(e);
      }
    } else {
      console.error('Missing permissions for clipboard-write');
    }
  });
});
chrome.storage.local.get(items => {
  if (typeof items === 'undefined') {
    console.error(chrome.runtime.lastError);
    return;
  }
  for (const key of Object.keys(checkboxFields)) {
    checkboxFields[key].checked =
      typeof items[key] !== 'undefined' ? items[key] : defaults[key];
  }
});
chrome.runtime.sendNativeMessage(
  'sh.tat.open_in_mpv',
  {
    init: true,
  },
  (/** @type InitResponse | null | undefined */ resp) => {
    if (!resp) {
      console.error(chrome.runtime.lastError);
      return;
    }
    logFile.innerText = resp.logPath;
    socket.innerText = resp.socketPath;
    version.innerText = resp.version;
  }
);
