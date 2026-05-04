"""
fix_saved_batch_view.py
Run from ~/Desktop/lister_web on dev branch:
    python3 fix_saved_batch_view.py
"""
src = open('templates/index.html').read()

# Find and replace the toggleSavedBatch start
old_start = """async function toggleSavedBatch(batchId, rowEl) {
  const next = rowEl.nextElementSibling;
  if (next && next.classList.contains('saved-batch-expanded')) {
    next.remove();
    return;
  }
  // Close any other open ones
  document.querySelectorAll('.saved-batch-expanded').forEach(el => el.remove());
  try {
    const r = await fetch(`/api/saved-batches/${batchId}`);
    if (!r.ok) throw new Error(await r.text());
    const data = await r.json();"""

new_start = """async function toggleSavedBatch(batchId, rowEl) {
  try {
    const r = await fetch(`/api/saved-batches/${batchId}`);
    if (!r.ok) throw new Error(await r.text());
    const data = await r.json();
    const dd = document.getElementById('saved-batches-dropdown');
    if (dd) dd.style.display = 'none';
    window._currentSavedBatch = data;
    renderSavedBatchInDashboard(data);
    return;
    /* OLD CODE BELOW - unreachable
"""

if old_start in src:
    src = src.replace(old_start, new_start, 1)
    print('patched toggleSavedBatch start')
else:
    print('NOT FOUND start')

# Find the end of the original block and close the comment
# Look for the closing curly of the function
old_end_marker = "}\n\nfunction toggleSavedBatchesDropdown"
new_end_marker = "*/\n}\n\nfunction toggleSavedBatchesDropdown"
if old_end_marker in src and "/* OLD CODE BELOW - unreachable" in src:
    src = src.replace(old_end_marker, new_end_marker, 1)
    print('closed comment')

# Add the render function before </script>
helper = """
function renderSavedBatchInDashboard(data) {
  const grid = document.querySelector('.tile-grid') || document.getElementById('listing-grid') || document.querySelector('.listings-grid');
  if (!grid) { console.warn('No grid found'); return; }
  let banner = document.getElementById('saved-batch-banner');
  if (banner) banner.remove();
  banner = document.createElement('div');
  banner.id = 'saved-batch-banner';
  banner.style.cssText = 'grid-column:1/-1;background:#1a3a1a;border:1px solid #2d5a2d;border-radius:8px;padding:14px 18px;display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;';
  const safeName = String(data.name||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  banner.innerHTML = '<div><div style="font-size:11px;color:#86efac;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;margin-bottom:2px;">Saved Batch</div><div style="font-size:15px;font-weight:700;color:#fff;">📁 ' + safeName + ' <span style="color:var(--muted);font-size:12px;font-weight:400;">· ' + data.items.length + ' items</span></div></div><button class="btn" onclick="exitSavedBatch()" style="background:transparent;border-color:var(--border);color:var(--text);font-size:13px;">← Back to Dashboard</button>';
  grid.innerHTML = '';
  grid.appendChild(banner);
  if (!data.items.length) {
    const empty = document.createElement('div');
    empty.style.cssText = 'grid-column:1/-1;text-align:center;padding:40px;color:var(--muted);';
    empty.textContent = 'This batch is empty';
    grid.appendChild(empty);
    return;
  }
  data.items.forEach(it => {
    const tile = document.createElement('div');
    tile.className = 'tile';
    tile.style.cssText = 'background:var(--card);border:1px solid var(--border);border-radius:10px;overflow:hidden;';
    const photoUrl = it.thumb_url || (it.photo_id ? '/api/photos/view/' + it.photo_id : '');
    const isNew = (it.condition || '').toUpperCase() === 'NEW';
    const condBadge = isNew
      ? '<span style="position:absolute;top:8px;left:8px;background:rgba(34,197,94,0.9);color:#000;font-size:10px;font-weight:700;padding:3px 8px;border-radius:4px;">NEW</span>'
      : '<span style="position:absolute;top:8px;left:8px;background:rgba(245,158,11,0.9);color:#000;font-size:10px;font-weight:700;padding:3px 8px;border-radius:4px;">USED</span>';
    const safeTitle = String(it.title || '(untitled)').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    const imgHtml = photoUrl ? '<img src="' + photoUrl + '" style="width:100%;height:100%;object-fit:cover;"/>' : '';
    tile.innerHTML = '<div style="position:relative;aspect-ratio:1;background:var(--bg);">' + imgHtml + condBadge + '</div><div style="padding:12px;"><div style="font-size:13px;font-weight:600;color:var(--text);margin-bottom:6px;line-height:1.3;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;">' + safeTitle + '</div><div style="font-size:18px;font-weight:800;color:#22c55e;">$' + (Number(it.price)||0).toFixed(2) + '</div></div>';
    grid.appendChild(tile);
  });
}

function exitSavedBatch() {
  window._currentSavedBatch = null;
  const banner = document.getElementById('saved-batch-banner');
  if (banner) banner.remove();
  if (typeof loadListings === 'function') loadListings();
  else if (typeof refresh === 'function') refresh();
  else location.reload();
}
"""

src = src.replace('</script>\n</body>', helper + '\n</script>\n</body>')

open('templates/index.html','w').write(src)
print('done')
