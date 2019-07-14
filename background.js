chrome.contextMenus.create({
  contexts: ['link'],
  title: 'Open in mpv',
  onclick: info => chrome.runtime.sendNativeMessage(
    'sh.tat.open_in_mpv',
    { url: info['linkUrl'] }
  )
});
