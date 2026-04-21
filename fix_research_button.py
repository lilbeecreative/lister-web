content = open('templates/auction.html').read()

old = "      <button class=\"btn-blue\" onclick=\"researchWatchlist()\">Research watchlist</button>"
new = "      <button class=\"btn-blue\" onclick=\"goToResearch()\">Research watchlist</button>"

if old in content:
    content = content.replace(old, new)
    print('✅ Button updated')
else:
    print('❌ not found')

old_fn = "async function researchWatchlist() {"
# Find and replace the whole researchWatchlist function
import re
match = re.search(r'async function researchWatchlist\(\) \{.*?\n\}', content, re.DOTALL)
if match:
    old_func = match.group(0)
    new_func = '''function goToResearch() {
  var watched = allItems.filter(function(i) { return i._watch; });
  if (!watched.length) { alert('No watchlisted items. Check the watch column on items first.'); return; }
  localStorage.setItem('auction_research_items', JSON.stringify(watched));
  localStorage.setItem('auction_research_scan_id', currentScanId||'');
  window.location.href = '/auction/research';
}'''
    content = content.replace(old_func, new_func)
    print('✅ Function replaced')
else:
    print('❌ Function not found')

open('templates/auction.html', 'w').write(content)
