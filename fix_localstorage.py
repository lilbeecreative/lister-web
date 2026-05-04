import re

with open('templates/auction.html', 'r', encoding='utf-8') as f:
    src = f.read()

# Find and replace the entire block from loadHistory to end of deleteScan
pattern = r'(function loadHistory\(\).*?function deleteScan\([^)]*\).*?\n})'
match = re.search(pattern, src, re.DOTALL)
if match:
    print(f"Found block at chars {match.start()}-{match.end()}")
    
    new_funcs = """async function loadHistory() {
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
      return '<div class="scan-item' + (s.id === currentScanId ? ' active' : '') + '" onclick="loadScan(\\'' + s.id + '\\')">' +
        '<div class="scan-item-del" onclick="event.stopPropagation();deleteScan(\\'' + s.id + '\\')">✕</div>' +
        '<div class="scan-item-title">' + esc(s.name) + '</div>' +
        '<div class="scan-item-meta">' + (s.items||[]).length + ' lots · ' + hvCount + ' high value</div>' +
        '</div>';
    }).join('');
  } catch(e) {
    el.innerHTML = '<div style="font-size:11px;color:#475569;text-align:center;padding:8px;">Error loading</div>';
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
  } catch(e) { console.warn('Save scan failed', e); }
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
  } catch(e) { console.warn('Load scan failed', e); }
}

async function deleteScan(id) {
  try {
    await fetch('/api/auction/scans/' + id, {method: 'DELETE'});
    if (currentScanId === id) { currentScanId = null; allItems = []; showUpload(); }
    loadHistory();
  } catch(e) { console.warn('Delete scan failed', e); }
}"""
    
    src = src[:match.start()] + new_funcs + src[match.end():]
    with open('templates/auction.html', 'w', encoding='utf-8') as f:
        f.write(src)
    print("patched")
else:
    print("not found - trying line-based approach")
    # Count localStorage occurrences to verify file is correct
    count = src.count('localStorage')
    print(f"localStorage occurrences: {count}")
