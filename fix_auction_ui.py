content = open('templates/auction.html').read()

# 1. Fix spacing - more padding/gap throughout
old = '.main{padding:20px;display:flex;flex-direction:column;gap:14px;overflow-y:auto;}'
new = '.main{padding:28px;display:flex;flex-direction:column;gap:20px;overflow-y:auto;}'
content = content.replace(old, new)

old = '.stats-row{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;}'
new = '.stats-row{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;}'
content = content.replace(old, new)

old = '.stat-card{background:#1e2535;border:1px solid #2d3348;border-radius:10px;padding:12px;text-align:center;}'
new = '.stat-card{background:#1e2535;border:2px solid #2d3348;border-radius:12px;padding:18px 12px;text-align:center;cursor:pointer;transition:border-color .15s;}'
content = content.replace(old, new)

old = '.stat-n{font-size:22px;font-weight:700;color:#f1f5f9;}'
new = '.stat-n{font-size:32px;font-weight:700;color:#f1f5f9;}'
content = content.replace(old, new)

old = '.stat-l{font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:.05em;margin-top:3px;}'
new = '.stat-l{font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:.05em;margin-top:6px;}'
content = content.replace(old, new)

# 2. Bigger text on table rows
old = '.tbl-head{display:grid;grid-template-columns:32px 54px 1fr 100px 44px 36px;padding:10px 14px;background:#161b28;border-bottom:1px solid #2d3348;font-size:10px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.06em;align-items:center;gap:8px;}'
new = '.tbl-head{display:grid;grid-template-columns:32px 60px 1fr 120px 50px 40px;padding:12px 18px;background:#161b28;border-bottom:1px solid #2d3348;font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.06em;align-items:center;gap:10px;}'
content = content.replace(old, new)

old = '.tbl-row{display:grid;grid-template-columns:32px 54px 1fr 100px 44px 36px;padding:10px 14px;border-bottom:1px solid #161b28;align-items:center;font-size:12px;gap:8px;transition:background .1s;}'
new = '.tbl-row{display:grid;grid-template-columns:32px 60px 1fr 120px 50px 40px;padding:14px 18px;border-bottom:1px solid #161b28;align-items:center;font-size:13px;gap:10px;transition:background .1s;}'
content = content.replace(old, new)

old = '.tbl-row.hv{background:rgba(239,159,39,.05);border-left:3px solid #EF9F27;padding-left:11px;}'
new = '.tbl-row.hv{background:rgba(239,159,39,.05);border-left:4px solid #EF9F27;padding-left:14px;}'
content = content.replace(old, new)

old = '.tbl-row.hv:hover{background:rgba(239,159,39,.1);}'
new = '.tbl-row.hv:hover{background:rgba(239,159,39,.1);}\n.tbl-row.hv.watched{border-left:4px solid #EF9F27;padding-left:14px;}'
content = content.replace(old, new)

old = '.tbl-row.watched{background:rgba(29,78,216,.07);border-left:3px solid #1d4ed8;padding-left:11px;}'
new = '.tbl-row.watched{background:rgba(29,78,216,.07);border-left:4px solid #1d4ed8;padding-left:14px;}'
content = content.replace(old, new)

old = '.item-name{font-weight:600;color:#f1f5f9;line-height:1.3;cursor:pointer;}'
new = '.item-name{font-weight:600;color:#f1f5f9;line-height:1.4;cursor:pointer;font-size:14px;}'
content = content.replace(old, new)

old = '.item-desc{font-size:10px;color:#64748b;margin-top:2px;}'
new = '.item-desc{font-size:11px;color:#64748b;margin-top:4px;line-height:1.4;}'
content = content.replace(old, new)

old = '.val-pill{display:inline-block;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700;white-space:nowrap;}'
new = '.val-pill{display:inline-block;padding:5px 14px;border-radius:20px;font-size:14px;font-weight:700;white-space:nowrap;}'
content = content.replace(old, new)

old = '.lot{color:#64748b;font-size:11px;white-space:nowrap;}'
new = '.lot{color:#64748b;font-size:13px;white-space:nowrap;font-weight:500;}'
content = content.replace(old, new)

# 3. Remove filter pills section from HTML
old_filter = '''      <div class="filter-bar">
        <button class="filter-pill active" id="f-all" onclick="setFilter(\'all\')">All</button>
        <button class="filter-pill" id="f-hv" onclick="setFilter(\'hv\')">High value</button>
        <button class="filter-pill" id="f-watch" onclick="setFilter(\'watch\')">Watchlist</button>
      </div>'''
new_filter = ''
content = content.replace(old_filter, new_filter)

# 4. Make stat cards clickable to filter - update JS updateStats
old_stats_js = '''  document.getElementById(\'stat-total\').textContent = allItems.length;
  document.getElementById(\'stat-hv\').textContent = hv;
  document.getElementById(\'stat-watch\').textContent = wl;
  // Update filter pills
  document.getElementById(\'f-all\').textContent = \'All (\' + allItems.length + \')\';
  document.getElementById(\'f-hv\').textContent = \'High value (\' + hv + \')\';
  document.getElementById(\'f-watch\').textContent = \'Watchlist (\' + wl + \')\';
  // Watch banner'''

new_stats_js = '''  document.getElementById(\'stat-total\').textContent = allItems.length;
  document.getElementById(\'stat-hv\').textContent = hv;
  document.getElementById(\'stat-watch\').textContent = wl;
  // Highlight active stat card
  document.querySelectorAll(\'.stat-card\').forEach(function(c){c.style.borderColor=\'#2d3348\';});
  if (currentFilter===\'all\') document.getElementById(\'stat-card-all\').style.borderColor=\'#475569\';
  if (currentFilter===\'hv\') document.getElementById(\'stat-card-hv\').style.borderColor=\'#854F0B\';
  if (currentFilter===\'watch\') document.getElementById(\'stat-card-watch\').style.borderColor=\'#1d4ed8\';
  // Watch banner'''

content = content.replace(old_stats_js, new_stats_js)

# 5. Add IDs and onclick to stat cards in HTML
old_stat_cards = '''      <div class="stats-row">
        <div class="stat-card"><div class="stat-n" id="stat-total">0</div><div class="stat-l">Items found</div></div>
        <div class="stat-card"><div class="stat-n amber" id="stat-hv">0</div><div class="stat-l">High value (&gt;$500)</div></div>
        <div class="stat-card"><div class="stat-n blue" id="stat-watch">0</div><div class="stat-l">Watchlisted</div></div>
      </div>'''

new_stat_cards = '''      <div class="stats-row">
        <div class="stat-card" id="stat-card-all" onclick="setFilter(\'all\')" style="border-color:#475569;"><div class="stat-n" id="stat-total">0</div><div class="stat-l">Items found</div></div>
        <div class="stat-card" id="stat-card-hv" onclick="setFilter(\'hv\')"><div class="stat-n amber" id="stat-hv">0</div><div class="stat-l">High value (&gt;$500)</div></div>
        <div class="stat-card" id="stat-card-watch" onclick="setFilter(\'watch\')"><div class="stat-n blue" id="stat-watch">0</div><div class="stat-l">Watchlisted</div></div>
      </div>'''

content = content.replace(old_stat_cards, new_stat_cards)

# 6. Update setFilter to highlight stat cards too
old_setfilter = '''function setFilter(f) {
  currentFilter = f;
  document.querySelectorAll(\'.filter-pill\').forEach(function(p) { p.className = \'filter-pill\'; });
  document.getElementById(\'f-\' + f).className = \'filter-pill \' + (f === \'watch\' ? \'active-blue\' : \'active\');
  renderItems();
}'''

new_setfilter = '''function setFilter(f) {
  currentFilter = f;
  updateStats();
  renderItems();
}'''

content = content.replace(old_setfilter, new_setfilter)

open('templates/auction.html', 'w').write(content)
print('done')
