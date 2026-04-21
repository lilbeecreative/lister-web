content = open('templates/auction.html').read()

# Add Research tab to sidebar after scan history
old_sidebar_bottom = '''    <div class="new-scan-btn" onclick="showUpload()">+ New scan</div>'''
new_sidebar_bottom = '''    <div style="margin-top:8px;border-top:1px solid #2d3348;padding-top:12px;">
      <div style="font-size:10px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;">Tools</div>
      <div class="sidebar-tool-btn" id="research-tab-btn" onclick="goToResearch()">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        Deep Research
        <span id="research-tab-count" style="display:none;background:#854F0B;color:#FAC775;font-size:10px;padding:1px 7px;border-radius:20px;margin-left:auto;"></span>
      </div>
    </div>
    <div class="new-scan-btn" onclick="showUpload()">+ New scan</div>'''

if old_sidebar_bottom in content:
    content = content.replace(old_sidebar_bottom, new_sidebar_bottom)
    print('✅ Research tab added to sidebar')
else:
    print('❌ not found')

# Add CSS for the tool button
old_css_end = '.new-scan-btn:hover{border-color:#475569;color:#94a3b8;}'
new_css_end = '''.new-scan-btn:hover{border-color:#475569;color:#94a3b8;}
.sidebar-tool-btn{display:flex;align-items:center;gap:8px;padding:9px 12px;border-radius:8px;border:1px solid #2d3348;background:#1e2535;color:#94a3b8;font-size:12px;font-weight:600;cursor:pointer;transition:all .15s;}
.sidebar-tool-btn:hover{background:#2d3348;color:#f1f5f9;border-color:#475569;}
.sidebar-tool-btn.has-items{border-color:#854F0B;color:#FAC775;background:rgba(65,36,2,.3);}'''
content = content.replace(old_css_end, new_css_end)

# Update goToResearch to also update the tab badge
old_goto = '''function goToResearch() {
  var watched = allItems.filter(function(i) { return i._watch; });
  if (!watched.length) { alert('No watchlisted items. Check the watch column on items first.'); return; }
  localStorage.setItem('auction_research_items', JSON.stringify(watched));
  localStorage.setItem('auction_research_scan_id', currentScanId||'');
  window.location.href = '/auction/research';
}'''

new_goto = '''function goToResearch() {
  var watched = allItems.filter(function(i) { return i._watch; });
  if (!watched.length) { alert('No watchlisted items. Check the watch column on items first.'); return; }
  localStorage.setItem('auction_research_items', JSON.stringify(watched));
  localStorage.setItem('auction_research_scan_id', currentScanId||'');
  window.location.href = '/auction/research';
}

function updateResearchTab() {
  var watched = allItems.filter(function(i) { return i._watch; });
  var btn = document.getElementById('research-tab-btn');
  var cnt = document.getElementById('research-tab-count');
  if (watched.length) {
    btn.classList.add('has-items');
    cnt.style.display = '';
    cnt.textContent = watched.length;
  } else {
    btn.classList.remove('has-items');
    cnt.style.display = 'none';
  }
}'''

content = content.replace(old_goto, new_goto)

# Call updateResearchTab from toggleWatch
old_toggle = '''function toggleWatch(id, checked) {
  var item = allItems.find(function(i) { return i._id === id; });
  if (item) { item._watch = checked; }
  updateStats();
  if (currentFilter === 'watch') renderItems();
  saveCurrentScan();
}'''

new_toggle = '''function toggleWatch(id, checked) {
  var item = allItems.find(function(i) { return i._id === id; });
  if (item) { item._watch = checked; }
  updateStats();
  updateResearchTab();
  if (currentFilter === 'watch') renderItems();
  saveCurrentScan();
}'''

content = content.replace(old_toggle, new_toggle)

open('templates/auction.html', 'w').write(content)
print('done')
