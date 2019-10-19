chrome.contextMenus.create({
  contexts: ['link', 'page', 'video', 'audio'],
  title: 'Open in mpv',
  onclick: info =>
    chrome.runtime.sendNativeMessage('sh.tat.open_in_mpv', {
      url: info['linkUrl'] || info['srcUrl'] || info['pageUrl']
    })
});
