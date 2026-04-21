content = open('templates/auction.html').read()

# 1. Fix title overlapping image - the item-name div needs proper overflow handling
# The image is in its own column but the title column needs min-width:0
old_item_detail = '(item._page_img ? \'<div><img class="thumb" src="\' + esc(item._page_img) + \'" onclick="openImgModal(\\\'\' + esc(item._page_img) + \'\\\')">\' : \'<div><div class="thumb-placeholder"><svg'
# Add min-width to the title cell
old_title_cell = "'<div>' +" + "\n      '<div class=\"item-name\"'"
new_title_cell = "'<div style=\"min-width:0;overflow:hidden\">' +" + "\n      '<div class=\"item-name\"'"
content = content.replace(old_title_cell, new_title_cell)

# 2. Add URL scan section to the upload view
old_upload_end = '''    </div>

    <div id="results-view"'''
new_upload_end = '''      <div style="margin-top:20px;">
        <div style="font-size:13px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px;">Or scan by URL</div>
        <div style="display:flex;gap:8px;">
          <input type="text" id="url-input" placeholder="Paste auction URL (Dickensheet, Purple Wave, etc.)" style="flex:1;background:#1e2535;border:1px solid #2d3348;border-radius:8px;padding:10px 14px;color:#f1f5f9;font-size:13px;font-family:inherit;outline:none;">
          <button class="btn-amber" onclick="startUrlScan()" style="white-space:nowrap;">Scan URL</button>
        </div>
        <div id="url-progress" style="display:none;margin-top:10px;background:#1e2535;border:1px solid #2d3348;border-radius:8px;padding:12px 14px;">
          <div style="font-size:12px;color:#EF9F27;font-weight:600;" id="url-status">Scanning URL...</div>
          <div style="height:4px;background:#2d3348;border-radius:2px;margin-top:8px;overflow:hidden;"><div id="url-bar" style="height:100%;background:#EF9F27;border-radius:2px;width:0%;transition:width 0.5s;"></div></div>
        </div>
      </div>
    </div>

    <div id="results-view"'''

if old_upload_end in content:
    content = content.replace(old_upload_end, new_upload_end)
    print('✅ URL scan added')
else:
    print('❌ upload end not found')

# 3. Add URL scan JS
old_js_end = "function esc(s){"
new_js_end = """async function startUrlScan() {
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
}

function esc(s){"""

content = content.replace(old_js_end, new_js_end)

open('templates/auction.html', 'w').write(content)
print('done')
