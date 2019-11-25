const qs = document.querySelector.bind(document);
const button = qs('#save');
const info = qs('#info');
const logFile = qs('#log-file');
const saved = qs('#saved');
const socket = qs('#socket');
const checkboxFields = {
  debugFlag: qs('#debug'),
  singleFlag: qs('#single')
};
const defaults = {
  debugFlag: false,
  singleFlag: true
};
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
