/**
 * This file is part of open-in-mpv.
 *
 * Copyright 2019 Andrew Udvare
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

const qs = document.querySelector.bind(document);
const button = qs('#save');
const checkboxFields = {
  debugFlag: qs('#debug'),
  singleFlag: qs('#single')
};
const defaults = {
  debugFlag: false,
  singleFlag: true
};
const info = qs('#info');
const logFile = qs('#log-file');
const saved = qs('#saved');
const socket = qs('#socket');
const WAIT_TIME = 5000;

button.addEventListener('mousedown', () => {
  const data = {};
  for (const key of Object.keys(checkboxFields)) {
    data[key] = checkboxFields[key].checked;
  }
  button.disabled = true;
  chrome.storage.local.set(data, () => {
    button.disabled = false;
    saved.classList.remove('hidden');
    setTimeout(() => saved.classList.add('hidden'), WAIT_TIME);
  });
});

chrome.storage.local.get(items => {
  for (const key of Object.keys(checkboxFields)) {
    checkboxFields[key].checked =
      typeof items[key] !== 'undefined' ? items[key] : defaults[key];
  }
});

chrome.runtime.sendNativeMessage(
  'sh.tat.open_in_mpv',
  {
    init: true
  },
  resp => {
    logFile.innerText = resp.dataPath;
    socket.innerText = resp.socketPath;
    info.classList.remove('hidden');
  }
);
