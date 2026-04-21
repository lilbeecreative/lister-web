content = open('templates/auction.html').read()

old_js = '''async function startUrlScan() {
  var url = document.getElementById('url-input').value.trim();
  if (!url) { alert('Please enter a URL'); return; }
  document.getElementById('url-progress').style.display = '';
  document.getElementById('url-bar').style.width = '30%';
  document.getElementById('url-status').textContent = 'Scraping auction page...';
  try {
    var r = await fetch('/api/auction/scan', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({url: url})
    });
    if (!r.ok) {
      var err = await r.json().catch(function(){return{};});
      alert('URL scan failed: ' + (err.detail || 'Unknown error'));
      document.getElementById('url-progress').style.display = 'none';
      return;
    }
    document.getElementById('url-bar').style.width = '60%';
    document.getElementById('url-status').textContent = 'Processing results...';
    var data = await r.json();
    document.getElementById('url-bar').style.width = '100%';
    document.getElementById('url-status').textContent = 'Complete!';
    setTimeout(function() { document.getElementById('url-progress').style.display = 'none'; }, 1500);
    // Show results in a new scan
    if (data.session_id) {
      alert('URL scan complete! Results saved as session: ' + data.session_id);
    }
  } catch(e) {
    alert('URL scan error: ' + e.message);
    document.getElementById('url-progress').style.display = 'none';
  }
}'''

new_js = '''async function startUrlScan() {
  var url = document.getElementById('url-input').value.trim();
  if (!url) { alert('Please enter a URL'); return; }
  document.getElementById('url-progress').style.display = '';
  document.getElementById('url-bar').style.width = '20%';
  document.getElementById('url-status').textContent = 'Scraping auction page...';
  try {
    var r = await fetch('/api/auction/scan', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({url: url})
    });
    if (!r.ok) {
      var err = await r.json().catch(function(){return{};});
      alert('URL scan failed: ' + (err.detail || 'Unknown error'));
      document.getElementById('url-progress').style.display = 'none';
      return;
    }
    var data = await r.json();
    var sessionId = data.session_id;
    document.getElementById('url-bar').style.width = '40%';
    document.getElementById('url-status').textContent = 'Processing items...';
    // Poll for completion
    var polls = 0;
    var pollInterval = setInterval(async function() {
      polls++;
      var pct = Math.min(40 + polls * 5, 90);
      document.getElementById('url-bar').style.width = pct + '%';
      try {
        var ir = await fetch('/api/auction/items/' + sessionId);
        var items = await ir.json();
        if (items && items.length > 0) {
          document.getElementById('url-status').textContent = 'Found ' + items.length + ' items...';
        }
        var sr = await fetch('/api/auction/sessions');
        var sessions = await sr.json();
        var session = sessions.find(function(s) { return s.session_id === sessionId; });
        if (session && session.status === 'done' || polls > 30) {
          clearInterval(pollInterval);
          document.getElementById('url-bar').style.width = '100%';
          document.getElementById('url-status').textContent = 'Complete! ' + (items ? items.length : 0) + ' items found';
          // Convert to auction scan format and save
          if (items && items.length) {
            var scanId = 'url_' + Date.now();
            var converted = items.map(function(item, i) {
              return {
                _id: 'item_' + i,
                lot: item.lot_number || String(i+1),
                title: item.title || item.description || 'Unknown Item',
                your_value: parseFloat(item.estimate || item.price || 0) || 0,
                notes: item.description || '',
                _watch: false,
                _page_img: item.image_url || ''
              };
            });
            currentScanId = scanId;
            scanName = url.split('/').pop() || 'URL Scan';
            allItems = converted;
            saveCurrentScan();
            setTimeout(function() {
              document.getElementById('url-progress').style.display = 'none';
              document.getElementById('upload-view').classList.add('hidden');
              document.getElementById('results-view').classList.remove('hidden');
              document.getElementById('progress-card').classList.add('hidden');
              document.getElementById('scan-title').textContent = scanName;
              updateStats();
              renderItems();
              loadHistory();
            }, 1000);
          }
        }
      } catch(e) { console.error(e); }
    }, 3000);
  } catch(e) {
    alert('URL scan error: ' + e.message);
    document.getElementById('url-progress').style.display = 'none';
  }
}'''

if old_js in content:
    content = content.replace(old_js, new_js)
    open('templates/auction.html', 'w').write(content)
    print('done')
else:
    print('not found')
