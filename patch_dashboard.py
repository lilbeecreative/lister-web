content = open('templates/index.html').read()
changes = 0

# 1. Replace tile-body with editable title + two search buttons + editable price + condition toggle
old_body = '''      <div class="tile-body">
        <a class="tile-title" href="https://www.google.com/search?q=${encodeURIComponent(l.title || '')}" target="_blank" rel="noopener" style="text-decoration:none;cursor:pointer;">${l.title || 'Unknown Item'} 🔍</a>
        <div class="tile-category">${l.ebay_category || ''}</div>
      </div>'''

new_body = '''      <div class="tile-body">
        <input class="tile-title-input" type="text" value="${(l.title||'').replace(/"/g,'&quot;')}" data-id="${l.id}" placeholder="Title">
        <div class="tile-search-btns">
          <button class="tile-search-btn" onclick="window.open('https://www.google.com/search?q='+encodeURIComponent(document.querySelector('.tile-title-input[data-id=&quot;${l.id}&quot;]').value),'_blank','noopener')">Google</button>
          <button class="tile-search-btn" onclick="window.open('https://www.ebay.com/sch/i.html?_nkw='+encodeURIComponent(document.querySelector('.tile-title-input[data-id=&quot;${l.id}&quot;]').value)+'&LH_Sold=1&LH_Complete=1','_blank','noopener')">eBay Sold</button>
        </div>
        <div class="tile-price-cond-row">
          <span style="color:var(--muted);font-size:11px;">$</span>
          <input class="tile-price-input" type="number" step="0.01" value="${l.price.toFixed(2)}" data-id="${l.id}">
          <div class="tile-cond-toggle">
            <button class="tile-cond-btn${isNew?'' :' active'}" data-id="${l.id}" data-cond="used">Used</button>
            <button class="tile-cond-btn${isNew?' active':''}" data-id="${l.id}" data-cond="new">New</button>
          </div>
        </div>
      </div>'''

if old_body in content:
    content = content.replace(old_body, new_body)
    changes += 1
    print('✅ Tile body updated')
else:
    print('❌ Tile body not found')

# 2. Add CSS for new elements (after .tile-controls style)
old_css = '.tile-controls { padding: 0 10px 10px; display: flex; gap: 6px; align-items: center; }'
new_css = '''.tile-controls { padding: 0 10px 10px; display: flex; gap: 6px; align-items: center; }
.tile-title-input { width:100%; background:transparent; border:none; border-bottom:1px solid transparent; color:#f8fafc; font-size:13px; font-weight:700; line-height:1.4; font-family:inherit; outline:none; padding:0 0 2px; margin-bottom:6px; transition:border-color 0.15s; }
.tile-title-input:hover { border-bottom-color:var(--border); }
.tile-title-input:focus { border-bottom-color:var(--accent); }
.tile-search-btns { display:flex; gap:5px; margin-bottom:6px; }
.tile-search-btn { flex:1; font-size:10px; padding:4px 6px; border-radius:5px; border:1px solid var(--border); background:transparent; color:var(--muted); cursor:pointer; font-family:inherit; font-weight:600; }
.tile-search-btn:hover { background:var(--border); color:var(--text); }
.tile-price-cond-row { display:flex; align-items:center; gap:6px; }
.tile-price-input { width:70px; background:transparent; border:none; border-bottom:1px solid var(--border); color:#f8fafc; font-size:14px; font-weight:800; font-family:inherit; outline:none; padding:0 0 2px; }
.tile-price-input:focus { border-bottom-color:var(--accent); }
.tile-cond-toggle { display:flex; margin-left:auto; border:1px solid var(--border); border-radius:5px; overflow:hidden; }
.tile-cond-btn { font-size:10px; padding:4px 8px; background:transparent; border:none; color:var(--muted); cursor:pointer; font-family:inherit; font-weight:600; }
.tile-cond-btn.active { background:var(--accent); color:#fff; }
.proc-bar-wrap { background:var(--surface); border:1px solid var(--border); border-radius:10px; padding:10px 14px; margin-bottom:14px; }
.proc-bar-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:7px; font-size:11px; color:var(--muted); font-weight:600; text-transform:uppercase; letter-spacing:0.06em; }
.proc-bar-track { height:5px; background:var(--border); border-radius:3px; overflow:hidden; margin-bottom:7px; }
.proc-bar-fill { height:100%; background:#16a34a; border-radius:3px; transition:width 0.5s; }
.proc-pills { display:flex; gap:5px; flex-wrap:wrap; }
.proc-pill { font-size:10px; padding:2px 8px; border-radius:20px; }
.proc-pill-done { background:rgba(22,163,74,0.15); color:#4ade80; }
.proc-pill-scan { background:rgba(245,158,11,0.15); color:#f59e0b; }'''

if old_css in content:
    content = content.replace(old_css, new_css)
    changes += 1
    print('✅ CSS added')
else:
    print('❌ CSS anchor not found')

# 3. Add processing bar before stats div
old_stats = '    <div class="stats">'
new_stats = '''    <div class="proc-bar-wrap" id="proc-bar-wrap" style="display:none">
      <div class="proc-bar-header">
        <span>Processing queue</span>
        <span id="proc-bar-count">0 of 0 done</span>
      </div>
      <div class="proc-bar-track"><div class="proc-bar-fill" id="proc-bar-fill" style="width:0%"></div></div>
      <div class="proc-pills">
        <span class="proc-pill proc-pill-done" id="proc-pill-done">0 complete</span>
        <span class="proc-pill proc-pill-scan" id="proc-pill-scan">0 scanning</span>
      </div>
    </div>
    <div class="stats">'''

if old_stats in content:
    content = content.replace(old_stats, new_stats, 1)
    changes += 1
    print('✅ Processing bar added')
else:
    print('❌ Stats div not found')

# 4. Add event delegation for new inputs after updateBatch function
old_fn = 'function cyclePhoto(id, dir) {'
new_fn = '''function initTileListeners() {
  document.getElementById('tile-grid').addEventListener('blur', function(e) {
    var el = e.target;
    if (el.classList.contains('tile-title-input')) {
      updateField(el.dataset.id, 'title', el.value);
    }
    if (el.classList.contains('tile-price-input')) {
      updateField(el.dataset.id, 'price', parseFloat(el.value));
    }
  }, true);
  document.getElementById('tile-grid').addEventListener('click', function(e) {
    var el = e.target;
    if (el.classList.contains('tile-cond-btn')) {
      var id = el.dataset.id, cond = el.dataset.cond;
      el.parentElement.querySelectorAll('.tile-cond-btn').forEach(function(b){b.classList.remove('active');});
      el.classList.add('active');
      updateField(id, 'condition', cond);
      // Update badge
      var badge = document.querySelector('#tile-'+id+' .tile-badge-tl');
      if (badge) { badge.textContent = cond.toUpperCase(); badge.style.color = cond==='new'?'#4ade80':'#60a5fa'; }
    }
  });
}

async function updateField(id, field, value) {
  try {
    await fetch('/api/listings/'+id, {
      method: 'PATCH',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({field: field, value: value})
    });
  } catch(e) { console.error(e); }
}

function updateProcBar(stats) {
  var total = stats.total || 0;
  var proc = stats.processing || 0;
  var done = total - proc;
  var wrap = document.getElementById('proc-bar-wrap');
  if (!wrap) return;
  if (proc > 0 || done > 0) {
    wrap.style.display = '';
    var pct = total > 0 ? Math.round(done/total*100) : 0;
    document.getElementById('proc-bar-fill').style.width = pct + '%';
    document.getElementById('proc-bar-count').textContent = done + ' of ' + total + ' done';
    document.getElementById('proc-pill-done').textContent = done + ' complete';
    document.getElementById('proc-pill-scan').textContent = proc + ' scanning';
  } else {
    wrap.style.display = 'none';
  }
}

function cyclePhoto(id, dir) {'''

if old_fn in content:
    content = content.replace(old_fn, new_fn)
    changes += 1
    print('✅ New functions added')
else:
    print('❌ cyclePhoto not found')

# 5. Call initTileListeners after loadBatch
old_call = 'loadBatch();'
new_call = 'loadBatch(); initTileListeners();'
if old_call in content and new_call not in content:
    content = content.replace(old_call, new_call, 1)
    changes += 1
    print('✅ initTileListeners called')

open('templates/index.html', 'w').write(content)
print(f'\n✅ Done — {changes} changes applied')
