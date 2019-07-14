const appID = 'sh.tat.open_in_mpv';

chrome.contextMenus.create({
  id: 'open_in_mpv_context',
  title: 'Open in mpv',
  contexts: ['link'],
  onclick: function (info, tab) {
    const url = info['linkUrl'];
    if (!url) {
      return;
    }
    chrome.runtime.sendNativeMessage(appID, { url: url }, function (resp) {
      console.log(resp);
    });
  }
});
