"""
fix_auction_cloud_scans.py
Run from ~/Desktop/lister_web:
    python3 fix_auction_cloud_scans.py

Replaces localStorage scan history with Supabase cloud storage.
"""

TEMPLATE = "templates/auction.html"

OLD_FUNCS = '''function loadHistory() {
  var scans = JSON.parse(localStorage.getItem('auction_scans') || '[]');
  var el = document.getElementById('scan-history');
  if (!scans.length) {
    el.innerHTML = '<div style="font-size:11px;color:#475569;text-align:center;padding:8px;">No scans yet</div>';
    return;
  }
  el.innerHTML = scans.map(function(s) {
    var hvCount = (s.items || []).filter(function(i) { return (i.your_value||0) >= 500; }).length;
    return '<div class="scan-item' + (s.id === currentScanId ? ' active' : '') + '" onclick="loadScan(\'' + s.id + '\')">' +
      '<div class="scan-item-del" onclick="event.stopPropagation();deleteScan(\'' + s.id + '\')">✕</div>' +
      '<div class="scan-item-title">' + esc(s.name) + '</div>' +
      '<div class="scan-item-meta">' + (s.items||[]).length + ' lots · ' + hvCount + ' high value</div>' +
      '</div>';
  }).join('');
}

function saveCurrentScan() {
  if (!currentScanId || !allItems.length) return;
  var scans = JSON.parse(localStorage.getItem('auction_scans') || '[]');
  var idx = scans.findIndex(function(s) { return s.id === currentScanId; });
  var scanObj = {id: currentScanId, name: scanName, items: allItems, ts: Date.now()};
  if (idx >= 0) scans[idx] = scanObj;
  else scans.unshift(scanObj);
  localStorage.setItem('auction_scans', JSON.stringify(scans));
  loadHistory();
}

function loadScan(id) {
  var scans = JSON.parse(localStorage.getItem('auction_scans') || '[]');
  var scan = scans.find(function(s) { return s.id === id; });
  if (!scan) return;
  currentScanId = id;
  scanName = scan.name;
  allItems = scan.items || [];
  document.getElementById('scan-title').textContent = scan.name;
  document.getElementById('upload-view').classList.add('hidden');
  document.getElementById('results-view').classList.remove('hidden');
  document.getElementById('progress-card').classList.add('hidden');
  updateStats();
  renderItems();
  loadHistory();
}

function deleteScan(id) {
  var scans = JSON.parse(localStorage.getItem('auction_scans') || '[]');
  scans = scans.filter(function(s) { return s.id !== id; });
  localStorage.setItem('auction_scans', JSON.stringify(scans));
  if (currentScanId === id) {
    currentScanId = null;
    allItems = [];
    showUpload();
  }
  loadHistory();
}'''

NEW_FUNCS = '''async function loadHistory() {
  var el = document.getElementById('scan-history');
  el.innerHTML = '<div style="font-size:11px;color:#475569;text-align:center;padding:8px;">Loading...</div>';
  try {
    var r = await fetch('/api/auction/scans');
    var data = await r.json();
    var scans = data.scans || [];
    if (!scans.length) {
      el.innerHTML = '<div style="font-size:11px;color:#475569;text-align:center;padding:8px;">No scans yet</div>';
      return;
    }
    el.innerHTML = scans.map(function(s) {
      var hvCount = (s.items || []).filter(function(i) { return (i.your_value||0) >= 500; }).length;
      return '<div class="scan-item' + (s.id === currentScanId ? ' active' : '') + '" onclick="loadScan(\'' + s.id + '\')">' +
        '<div class="scan-item-del" onclick="event.stopPropagation();deleteScan(\'' + s.id + '\')">✕</div>' +
        '<div class="scan-item-title">' + esc(s.name) + '</div>' +
        '<div class="scan-item-meta">' + (s.items||[]).length + ' lots · ' + hvCount + ' high value</div>' +
        '</div>';
    }).join('');
  } catch(e) {
    el.innerHTML = '<div style="font-size:11px;color:#475569;text-align:center;padding:8px;">Error loading scans</div>';
  }
}

async function saveCurrentScan() {
  if (!currentScanId || !allItems.length) return;
  try {
    await fetch('/api/auction/scans', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({id: currentScanId, name: scanName, items: allItems})
    });
    loadHistory();
  } catch(e) {
    console.warn('Save scan failed', e);
  }
}

async function loadScan(id) {
  try {
    var r = await fetch('/api/auction/scans/' + id);
    var scan = await r.json();
    if (!scan || !scan.id) return;
    currentScanId = scan.id;
    scanName = scan.name;
    allItems = scan.items || [];
    document.getElementById('scan-title').textContent = scan.name;
    document.getElementById('upload-view').classList.add('hidden');
    document.getElementById('results-view').classList.remove('hidden');
    document.getElementById('progress-card').classList.add('hidden');
    updateStats();
    renderItems();
    loadHistory();
  } catch(e) {
    console.warn('Load scan failed', e);
  }
}

async function deleteScan(id) {
  try {
    await fetch('/api/auction/scans/' + id, {method: 'DELETE'});
    if (currentScanId === id) {
      currentScanId = null;
      allItems = [];
      showUpload();
    }
    loadHistory();
  } catch(e) {
    console.warn('Delete scan failed', e);
  }
}'''

def main():
    with open(TEMPLATE, "r", encoding="utf-8") as f:
        src = f.read()

    if OLD_FUNCS in src:
        src = src.replace(OLD_FUNCS, NEW_FUNCS, 1)
        print("✅ Replaced localStorage scan functions with Supabase API calls")
    else:
        print("❌ Could not find localStorage functions — may need manual patch")

    with open(TEMPLATE, "w", encoding="utf-8") as f:
        f.write(src)

    print("\nNow add backend endpoints to main.py, then:")
    print("   python3 -c \"import py_compile; py_compile.compile('main.py'); print('OK')\"")
    print("   git add main.py templates/auction.html")
    print('   git commit -m "cloud sync auction scan history via Supabase"')
    print("   git push")

if __name__ == "__main__":
    main()
