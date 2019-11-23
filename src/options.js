const qs = document.querySelector.bind(document);

const fields = {
  singleFlag: qs("#single"),
  debugFlag: qs("#debug")
};
const defaults = {
  singleFlag: true,
  debugFlag: false
};
const button = qs("#save");
const logFile = qs("#log-file");
const socket = qs("#socket");
const info = qs("#info");
const saved = qs('#saved');

button.addEventListener("mousedown", () => {
  const data = {};
  for (const key of Object.keys(fields)) {
    const field = fields[key];
    const value = field.type === "checkbox" ? field.checked : field.value;
    data[key] = value;
  }
  button.disabled = true;
  chrome.storage.local.set(data, () => {
    button.disabled = false;
    saved.classList.remove('hidden');
    setTimeout(() => saved.classList.add('hidden'), 5000);
  });
});

chrome.storage.local.get(items => {
  for (const key of Object.keys(fields)) {
    fields[key].checked =
      typeof items[key] !== "undefined" ? items[key] : defaults[key];
  }
});

chrome.runtime.sendNativeMessage(
  "sh.tat.open_in_mpv",
  {
    init: true
  },
  resp => {
    logFile.innerText = resp.dataPath;
    socket.innerText = resp.socketPath;
    info.classList.remove("hidden");
  }
);
