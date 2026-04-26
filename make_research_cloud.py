"""
make_research_cloud.py
Run from ~/Desktop/lister_web:
    python3 make_research_cloud.py

Makes deep research fully cloud-based:
- goToResearch() saves watchlist to Supabase, redirects to /auction/research?scan=ID
- Research page loads items from Supabase via scan ID in URL
- Results auto-save to Supabase on complete
- Any user opening the same URL sees the same results
"""
import sys

MAIN   = "main.py"
AHTML  = "templates/auction.html"
RHTML  = "templates/auction_research.html"

# ── 1. Backend: endpoint to get items for a scan_id ──────────────
BACKEND_ANCHOR = '@app.post("/api/auction/save-research")'

BACKEND_INSERT = '''
@app.get("/api/auction/research-items/{scan_id}")
async def get_research_items(scan_id: str):
    """Return watchlisted items for a scan so any client can load them."""
    import json
    try:
        row = supabase.table("auction_research_sessions") \
            .select("items,results,title").eq("share_id", scan_id).single().execute()
        data = row.data
        return {
            "scan_id": scan_id,
            "title":   data.get("title",""),
            "items":   json.loads(data.get("items","[]")),
            "results": json.loads(data.get("results","{}")),
        }
    except Exception:
        return {"scan_id": scan_id, "items": [], "results": {}}


'''

# ── 2. auction.html: save watchlist to Supabase before redirecting
OLD_GO_RESEARCH = """  if (!watched.length) { alert('No watchlisted items. Check the watch column on items first.'); return; }
  localStorage.setItem('auction_research_items', JSON.stringify(watched));
  localStorage.setItem('auction_research_scan_id', currentScanId||'');
  window.location.href = '/auction/research';"""

NEW_GO_RESEARCH = """  if (!watched.length) { alert('No watchlisted items. Check the watch column on items first.'); return; }
  var scanId = currentScanId || ('scan-' + Date.now());
  // Save to Supabase so any user/device can load it
  fetch('/api/auction/save-research', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({share_id: scanId, title: 'Scan ' + scanId, items: watched, results: {}})
  }).then(function(){
    window.location.href = '/auction/research?scan=' + encodeURIComponent(scanId);
  }).catch(function(){
    // Fallback to localStorage if save fails
    localStorage.setItem('auction_research_items', JSON.stringify(watched));
    localStorage.setItem('auction_research_scan_id', scanId);
    window.location.href = '/auction/research';
  });"""

# ── 3. auction_research.html: load from Supabase via ?scan= param
OLD_INIT = """function init() {
  var data = localStorage.getItem('auction_research_items');
  if (!data) {
    document.getElementById('empty-msg').textContent = 'No watchlisted items found. Go back and add items to your watchlist.';
    return;
  }
  try {
    watchItems = JSON.parse(data);
  } catch(e) {
    document.getElementById('empty-msg').textContent = 'Error loading items.';
    return;
  }
  if (!watchItems.length) {
    document.getElementById('empty-msg').textContent = 'No watchlisted items. Go back and check the watch column on items.';
    return;
  }
  document.getElementById('page-sub').textContent = watchItems.length + ' items to research';
  document.getElementById('start-btn').disabled = false;
  renderCards();
}"""

NEW_INIT = """function getScanId() {
  var params = new URLSearchParams(window.location.search);
  return params.get('scan') || localStorage.getItem('auction_research_scan_id') || '';
}

function init() {
  var scanId = getScanId();
  if (scanId) {
    fetch('/api/auction/research-items/' + encodeURIComponent(scanId))
      .then(function(r){ return r.json(); })
      .then(function(d){
        watchItems = d.items || [];
        if (d.results && Object.keys(d.results).length) {
          results = d.results;
        }
        if (!watchItems.length) {
          document.getElementById('empty-msg').textContent = 'No items found for this scan. Go back and watchlist some items.';
          return;
        }
        document.getElementById('page-sub').textContent = watchItems.length + ' items to research';
        document.getElementById('start-btn').disabled = false;
        // If results already exist, show export + share buttons
        if (Object.keys(results).length) {
          document.getElementById('export-btn').style.display = '';
          document.getElementById('share-btn').style.display = '';
        }
        renderCards();
      })
      .catch(function(){
        // Fallback to localStorage
        var data = localStorage.getItem('auction_research_items');
        if (data) { try { watchItems = JSON.parse(data); } catch(e){} }
        if (!watchItems.length) {
          document.getElementById('empty-msg').textContent = 'No watchlisted items found. Go back and add items to your watchlist.';
          return;
        }
        document.getElementById('page-sub').textContent = watchItems.length + ' items to research';
        document.getElementById('start-btn').disabled = false;
        renderCards();
      });
  } else {
    // No scan ID at all — legacy localStorage fallback
    var data = localStorage.getItem('auction_research_items');
    if (!data) {
      document.getElementById('empty-msg').textContent = 'No watchlisted items found. Go back and add items to your watchlist.';
      return;
    }
    try { watchItems = JSON.parse(data); } catch(e) {
      document.getElementById('empty-msg').textContent = 'Error loading items.';
      return;
    }
    if (!watchItems.length) {
      document.getElementById('empty-msg').textContent = 'No watchlisted items. Go back and check the watch column on items.';
      return;
    }
    document.getElementById('page-sub').textContent = watchItems.length + ' items to research';
    document.getElementById('start-btn').disabled = false;
    renderCards();
  }
}"""

# ── 4. saveResults: use scan_id from URL ─────────────────────────
OLD_SAVE_ID = "  var scanId = localStorage.getItem('auction_research_scan_id');"
NEW_SAVE_ID = "  var scanId = getScanId();"


def patch(path, replacements):
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    ok = True
    for old, new, label in replacements:
        if old in src:
            src = src.replace(old, new, 1)
            print(f"✅ Patched: {label}")
        else:
            print(f"❌ Not found: {label}")
            ok = False
    with open(path, "w", encoding="utf-8") as f:
        f.write(src)
    return ok


def main():
    try:
        patch(MAIN, [
            (BACKEND_ANCHOR, BACKEND_INSERT + BACKEND_ANCHOR, "research-items endpoint"),
        ])
        patch(AHTML, [
            (OLD_GO_RESEARCH, NEW_GO_RESEARCH, "goToResearch cloud save"),
        ])
        patch(RHTML, [
            (OLD_INIT,    NEW_INIT,    "init() cloud load"),
            (OLD_SAVE_ID, NEW_SAVE_ID, "saveResults scan ID"),
        ])
    except FileNotFoundError as e:
        print(f"❌ File not found: {e} — run from ~/Desktop/lister_web")
        sys.exit(1)

    print("\nNow run:")
    print("   git add main.py templates/auction.html templates/auction_research.html")
    print('   git commit -m "cloud-based research: load/save via Supabase, shared across all users"')
    print("   git push")

if __name__ == "__main__":
    main()
