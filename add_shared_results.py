"""
add_shared_results.py
Run from ~/Desktop/lister_web:
    python3 add_shared_results.py

Adds:
  Backend — POST /api/auction/save-research   (save results to Supabase)
            GET  /api/auction/load-research/{share_id}  (load by share ID)
  Frontend — auto-save on complete, share button with copyable link
"""
import sys, re

MAIN = "main.py"
HTML = "templates/auction_research.html"

# ── 1. BACKEND: save + load endpoints ────────────────────────────

BACKEND_ANCHOR = '@app.post("/api/auction/research-export")'

BACKEND_INSERT = '''
@app.post("/api/auction/save-research")
async def save_research(request: Request):
    import json, uuid
    body = await request.json()
    share_id = body.get("share_id") or str(uuid.uuid4())[:8]
    title    = body.get("title", "Auction Research")
    items    = body.get("items", [])
    results  = body.get("results", {})
    try:
        supabase.table("auction_research_sessions").upsert({
            "share_id": share_id,
            "title":    title,
            "items":    json.dumps(items),
            "results":  json.dumps(results),
        }, on_conflict="share_id").execute()
    except Exception as e:
        raise HTTPException(500, f"Save failed: {e}")
    return {"share_id": share_id}


@app.get("/api/auction/load-research/{share_id}")
async def load_research(share_id: str):
    import json
    try:
        row = supabase.table("auction_research_sessions") \
            .select("*").eq("share_id", share_id).single().execute()
        data = row.data
        return {
            "share_id": data["share_id"],
            "title":    data.get("title", ""),
            "items":    json.loads(data.get("items", "[]")),
            "results":  json.loads(data.get("results", "{}")),
        }
    except Exception as e:
        raise HTTPException(404, f"Session not found: {e}")


'''

# ── 2. FRONTEND patches ───────────────────────────────────────────

# 2a. Add share button next to export button in header
OLD_EXPORT_BTN = '<button class="btn-ghost" id="export-btn" onclick="exportResults()" style="display:none;">Export results</button>'
NEW_EXPORT_BTN = '<button class="btn-ghost" id="export-btn" onclick="exportResults()" style="display:none;">Export results</button>\n    <button class="btn-ghost" id="share-btn" onclick="shareResults()" style="display:none;">🔗 Share results</button>'

# 2b. Replace saveResults() to also push to Supabase
OLD_SAVE = """function saveResults() {
  var scanId = localStorage.getItem('auction_research_scan_id');
  if (!scanId) return;
  var scans = JSON.parse(localStorage.getItem('auction_scans')||'[]');
  var scan = scans.find(function(s){return s.id===scanId;});
  if (!scan) return;
  scan.items = scan.items.map(function(item) {
    var res = results[item.lot];
    if (res && res.type === 'result') {
      item.your_value = res.revised_value || item.your_value;
      item.notes = res.notes || item.notes;
      item._deep = true;
    }
    return item;
  });
  localStorage.setItem('auction_scans', JSON.stringify(scans));
}"""

NEW_SAVE = """function saveResults() {
  var scanId = localStorage.getItem('auction_research_scan_id');
  if (!scanId) return;
  var scans = JSON.parse(localStorage.getItem('auction_scans')||'[]');
  var scan = scans.find(function(s){return s.id===scanId;});
  if (!scan) return;
  scan.items = scan.items.map(function(item) {
    var res = results[item.lot];
    if (res && res.type === 'result') {
      item.your_value = res.revised_value || item.your_value;
      item.notes = res.notes || item.notes;
      item._deep = true;
    }
    return item;
  });
  localStorage.setItem('auction_scans', JSON.stringify(scans));
  // Push to Supabase for sharing
  var shareId = localStorage.getItem('auction_share_id_' + scanId);
  fetch('/api/auction/save-research', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({
      share_id: shareId || undefined,
      title: scan.name || scanId,
      items: watchItems,
      results: results
    })
  }).then(function(r){ return r.json(); }).then(function(d){
    if (d.share_id) {
      localStorage.setItem('auction_share_id_' + scanId, d.share_id);
      document.getElementById('share-btn').style.display = '';
    }
  }).catch(function(){});
}

function shareResults() {
  var scanId = localStorage.getItem('auction_research_scan_id');
  var shareId = scanId ? localStorage.getItem('auction_share_id_' + scanId) : null;
  if (!shareId) { alert('Save not ready yet — try again in a moment'); return; }
  var url = window.location.origin + '/auction/research/' + shareId;
  navigator.clipboard.writeText(url).then(function(){
    var btn = document.getElementById('share-btn');
    btn.textContent = '✓ Link copied!';
    setTimeout(function(){ btn.textContent = '🔗 Share results'; }, 2500);
  }).catch(function(){ prompt('Copy this link:', url); });
}"""

# 2c. Add init() check for share_id in URL to load from Supabase
OLD_INIT_END = """  document.getElementById('page-sub').textContent = watchItems.length + ' items to research';
  document.getElementById('start-btn').disabled = false;
  renderCards();
}"""

NEW_INIT_END = """  document.getElementById('page-sub').textContent = watchItems.length + ' items to research';
  document.getElementById('start-btn').disabled = false;
  renderCards();
}

function tryLoadShared() {
  var parts = window.location.pathname.split('/');
  var shareId = parts[parts.length - 1];
  // Only treat as share ID if it's 8 hex chars (uuid short)
  if (!/^[a-f0-9]{8}$/.test(shareId)) return false;
  fetch('/api/auction/load-research/' + shareId)
    .then(function(r){ if(!r.ok) throw new Error('not found'); return r.json(); })
    .then(function(d){
      watchItems = d.items || [];
      results = d.results || {};
      document.getElementById('page-sub').textContent = watchItems.length + ' items (shared view)';
      document.getElementById('start-btn').disabled = true;
      document.getElementById('start-btn').style.display = 'none';
      document.getElementById('export-btn').style.display = '';
      document.getElementById('empty-msg').style.display = 'none';
      renderCards();
    })
    .catch(function(){ init(); });
  return true;
}"""

# 2d. Replace window.onload to try shared first
OLD_ONLOAD = "window.addEventListener('DOMContentLoaded', init);"
NEW_ONLOAD = "window.addEventListener('DOMContentLoaded', function(){ if(!tryLoadShared()) init(); });"


def patch_main():
    with open(MAIN, "r", encoding="utf-8") as f:
        src = f.read()
    if BACKEND_ANCHOR not in src:
        print(f"❌ Could not find anchor in {MAIN}")
        return False
    src = src.replace(BACKEND_ANCHOR, BACKEND_INSERT + BACKEND_ANCHOR, 1)
    with open(MAIN, "w", encoding="utf-8") as f:
        f.write(src)
    print(f"✅ Patched {MAIN} — save-research + load-research endpoints added")
    return True


def patch_html():
    with open(HTML, "r", encoding="utf-8") as f:
        src = f.read()
    ok = True
    for old, new, label in [
        (OLD_EXPORT_BTN, NEW_EXPORT_BTN, "share button"),
        (OLD_SAVE,       NEW_SAVE,       "saveResults + shareResults"),
        (OLD_INIT_END,   NEW_INIT_END,   "tryLoadShared"),
        (OLD_ONLOAD,     NEW_ONLOAD,     "DOMContentLoaded"),
    ]:
        if old in src:
            src = src.replace(old, new, 1)
            print(f"✅ Patched {label}")
        else:
            print(f"❌ Could not find: {label}")
            ok = False
    with open(HTML, "w", encoding="utf-8") as f:
        f.write(src)
    return ok


def main():
    try:
        ok1 = patch_main()
        ok2 = patch_html()
    except FileNotFoundError as e:
        print(f"❌ File not found: {e} — run from ~/Desktop/lister_web")
        sys.exit(1)

    print("\n⚠️  You also need to create the Supabase table (run once in Supabase SQL editor):")
    print("""
create table if not exists auction_research_sessions (
  share_id  text primary key,
  title     text,
  items     text,
  results   text,
  created_at timestamptz default now()
);
""")
    print("Then:")
    print("   git add main.py templates/auction_research.html")
    print('   git commit -m "shared research results via Supabase"')
    print("   git push")

if __name__ == "__main__":
    main()
