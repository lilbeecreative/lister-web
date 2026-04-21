content = open('templates/index.html').read()
changes = 0

# 1. Add nav button CSS color
old_css = '.nav-btn[data-tab="settings"].active { background: #475569; }'
new_css = '''.nav-btn[data-tab="settings"].active { background: #475569; }
.nav-btn[data-tab="fastscan"].active { background: #16a34a; }
.fastscan-zone { border: 2px dashed var(--border); border-radius: 12px; padding: 32px; text-align: center; cursor: pointer; transition: border-color 0.15s; position: relative; overflow: hidden; }
.fastscan-zone:hover { border-color: #16a34a; }
.fastscan-zone input[type=file] { position: absolute; inset: 0; opacity: 0; cursor: pointer; width: 100%; height: 100%; font-size: 0; }
.fastscan-icon { font-size: 2.5rem; margin-bottom: 10px; }
.fastscan-title { font-size: 18px; font-weight: 800; color: var(--text); margin-bottom: 6px; }
.fastscan-sub { font-size: 13px; color: var(--muted); }
.fastscan-queue { display: flex; flex-direction: column; gap: 6px; margin-top: 16px; }
.fastscan-item { display: flex; align-items: center; gap: 10px; padding: 8px 12px; background: var(--card); border: 1px solid var(--border); border-radius: 8px; font-size: 12px; }
.fastscan-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.fs-dot-queue { background: #475569; }
.fs-dot-upload { background: #f59e0b; animation: pulse 1s infinite; }
.fs-dot-done { background: #16a34a; }
.fs-dot-err { background: var(--red); }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
.fastscan-progress { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 12px 14px; margin-top: 12px; }
.fastscan-progress-bar { height: 5px; background: var(--border); border-radius: 3px; overflow: hidden; margin: 8px 0; }
.fastscan-progress-fill { height: 100%; background: #16a34a; border-radius: 3px; transition: width 0.4s; }
.fastscan-cond { display: flex; gap: 8px; margin-bottom: 16px; }
.fastscan-cond-btn { flex: 1; padding: 10px; border-radius: 8px; border: 1px solid var(--border); background: transparent; color: var(--muted); font-family: inherit; font-size: 13px; font-weight: 600; cursor: pointer; }
.fastscan-cond-btn.active { background: #16a34a; border-color: #16a34a; color: #fff; }'''

if old_css in content:
    content = content.replace(old_css, new_css)
    changes += 1
    print('✅ CSS added')
else:
    print('❌ CSS anchor not found')

# 2. Add nav button
old_nav = '  <button class="nav-btn" data-tab="upload">📸 Upload</button>'
new_nav = '''  <button class="nav-btn" data-tab="upload">📸 Upload</button>
  <button class="nav-btn" data-tab="fastscan">⚡ Fast Scan</button>'''

if old_nav in content:
    content = content.replace(old_nav, new_nav)
    changes += 1
    print('✅ Nav button added')
else:
    print('❌ Nav button not found')

# 3. Add tab content before auction tab
old_tab = '  <!-- AUCTION TAB -->'
new_tab = '''  <!-- FAST SCAN TAB -->
  <div class="tab-content" id="tab-fastscan">
    <div style="padding:1.5rem 0 1rem;text-align:center;">
      <div style="font-size:2.5rem;margin-bottom:10px;">⚡</div>
      <div style="font-size:20px;font-weight:800;color:var(--text);margin-bottom:6px;">Fast Scan</div>
      <div style="font-size:13px;color:var(--muted);">Select multiple photos — each becomes its own listing.</div>
    </div>
    <div class="fastscan-cond">
      <button class="fastscan-cond-btn" id="fs-cond-new" onclick="setFsCond('new')">✓ New</button>
      <button class="fastscan-cond-btn" id="fs-cond-used" onclick="setFsCond('used')">Used</button>
    </div>
    <div class="fastscan-zone" id="fastscan-zone">
      <input type="file" id="fastscan-input" accept="image/*,image/heic" multiple onchange="startFastScan(this)">
      <div class="fastscan-icon">📷</div>
      <div class="fastscan-title">Select photos from gallery</div>
      <div class="fastscan-sub">Each photo will be scanned as a separate item</div>
    </div>
    <div id="fastscan-progress" style="display:none;" class="fastscan-progress">
      <div style="display:flex;justify-content:space-between;font-size:11px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:0.06em;">
        <span>Processing</span>
        <span id="fs-count">0 / 0</span>
      </div>
      <div class="fastscan-progress-bar"><div class="fastscan-progress-fill" id="fs-bar" style="width:0%"></div></div>
    </div>
    <div class="fastscan-queue" id="fastscan-queue"></div>
  </div>

  <!-- AUCTION TAB -->'''

if old_tab in content:
    content = content.replace(old_tab, new_tab)
    changes += 1
    print('✅ Tab content added')
else:
    print('❌ Tab anchor not found')

# 4. Add JS before closing script
old_js = '// ── INIT ───────────────────────────────────────────────────────'
new_js = '''// ── FAST SCAN ─────────────────────────────────────────────────
var fsCond = 'new';

function setFsCond(c) {
  fsCond = c;
  document.getElementById('fs-cond-new').className = 'fastscan-cond-btn' + (c==='new' ? ' active' : '');
  document.getElementById('fs-cond-used').className = 'fastscan-cond-btn' + (c==='used' ? ' active' : '');
}
setFsCond('new');

async function startFastScan(input) {
  const files = Array.from(input.files);
  if (!files.length) return;
  document.getElementById('fastscan-progress').style.display = '';
  const queue = document.getElementById('fastscan-queue');
  queue.innerHTML = '';
  const items = files.map((f, i) => {
    const el = document.createElement('div');
    el.className = 'fastscan-item';
    el.id = 'fs-item-' + i;
    el.innerHTML = '<div class="fastscan-dot fs-dot-queue"></div><div style="flex:1;color:var(--muted);">Photo ' + (i+1) + '</div><span style="font-size:10px;color:var(--muted);">Queued</span>';
    queue.appendChild(el);
    return el;
  });
  for (let i = 0; i < files.length; i++) {
    const el = items[i];
    el.innerHTML = '<div class="fastscan-dot fs-dot-upload"></div><div style="flex:1;">Photo ' + (i+1) + '</div><span style="font-size:10px;color:#f59e0b;">Uploading...</span>';
    try {
      // Create group
      const gr = await api('POST', '/api/groups', {session_id: crypto.randomUUID(), condition: fsCond});
      const gid = gr.group_id || gr.id;
      // Compress and upload
      const blob = await compressForUpload(files[i]);
      const fd = new FormData();
      fd.append('file', blob, 'photo_0.jpg');
      fd.append('group_id', gid);
      await fetch('/api/photos/upload', {method:'POST', body: fd});
      // Submit
      await api('POST', '/api/groups/submit', {group_id: gid, condition: fsCond, quantity: 1});
      el.innerHTML = '<div class="fastscan-dot fs-dot-done"></div><div style="flex:1;">Photo ' + (i+1) + '</div><span style="font-size:10px;color:#4ade80;">Submitted</span>';
    } catch(e) {
      el.innerHTML = '<div class="fastscan-dot fs-dot-err"></div><div style="flex:1;">Photo ' + (i+1) + '</div><span style="font-size:10px;color:var(--red);">Failed</span>';
    }
    const pct = Math.round((i+1)/files.length*100);
    document.getElementById('fs-bar').style.width = pct + '%';
    document.getElementById('fs-count').textContent = (i+1) + ' / ' + files.length;
  }
  input.value = '';
}

async function compressForUpload(file) {
  return new Promise(resolve => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();
    const url = URL.createObjectURL(file);
    img.onload = () => {
      let w = img.width, h = img.height, max = 1600;
      if (w > max || h > max) { if (w > h) { h = Math.round(h*max/w); w = max; } else { w = Math.round(w*max/h); h = max; } }
      canvas.width = w; canvas.height = h;
      ctx.drawImage(img, 0, 0, w, h);
      URL.revokeObjectURL(url);
      canvas.toBlob(resolve, 'image/jpeg', 0.88);
    };
    img.src = url;
  });
}

// ── INIT ───────────────────────────────────────────────────────'''

if old_js in content:
    content = content.replace(old_js, new_js)
    changes += 1
    print('✅ Fast scan JS added')
else:
    print('❌ JS anchor not found')

open('templates/index.html', 'w').write(content)
print(f'\n✅ Done — {changes} changes applied')
