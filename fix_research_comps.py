content = open('templates/auction_research.html').read()

# Replace comps section with simple eBay button
old_comps = '''        (compsHtml ? '<div><div class="section-lbl">Comparable sales</div><div class="comps-list">' + compsHtml + '</div></div>' : '') +'''
new_comps = '''        '<div><a href="https://www.ebay.com/sch/i.html?_nkw=' + encodeURIComponent((item.title||'').replace(/[,\\s]*\\(\\d+\\)[,\\s]*/g,\' \').replace(/\\bQTY\\s*\\(?\\d+\\)?/gi,\'\').trim()) + \'&LH_Sold=1&LH_Complete=1\' + \'" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:8px;background:#1e2535;border:1px solid #2d3348;border-radius:8px;padding:9px 14px;color:#94a3b8;font-size:12px;font-weight:600;text-decoration:none;">Search eBay Sold Listings ↗</a></div>' +'''

if old_comps in content:
    content = content.replace(old_comps, new_comps)
    print('✅ comps replaced')
else:
    print('❌ not found')

# Also remove the comps building code since we don't need it
old_comps_build = '''    var compsHtml = (res.comps||[]).map(function(c) {
      var itemTitle = item.title || '';
      var ebaySearch = 'https://www.ebay.com/sch/i.html?_nkw=' + encodeURIComponent(itemTitle) + '&LH_Sold=1&LH_Complete=1';
      return '<div class=\"comp-row\" style=\"cursor:pointer\" onclick=\"window.open(\\'' + ebaySearch + '\\',\\'_blank\\',\\'noopener,width=1200,height=800\\')\"><div class=\"comp-title\">' + esc(c.title||'') + '</div><div class=\"comp-price\">' + (c.price ? '$' + parseInt(c.price).toLocaleString() : 'N/A') + '</div><div class=\"comp-date\">' + esc(c.date||'') + '</div><div class=\"comp-src\">eBay Sold ↗</div></div>';
    }).join('');'''
new_comps_build = ''
if old_comps_build in content:
    content = content.replace(old_comps_build, new_comps_build)
    print('✅ comps build removed')
else:
    print('❌ comps build not found')

open('templates/auction_research.html', 'w').write(content)
