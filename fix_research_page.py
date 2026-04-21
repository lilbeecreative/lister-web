content = open('templates/auction_research.html').read()

# 1. Fix image - use item._page_img before research, res image after
old_img = '''    var imgHtml = res.image_url
      ? '<img src="' + esc(res.image_url) + '" alt="">'
      : '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>';
    var imgLabel = res.has_image ? 'Lot image analyzed' : 'No image available';'''

new_img = '''    var pageImg = item._page_img || '';
    var imgHtml = pageImg
      ? '<img src="' + esc(pageImg) + '" alt="" style="width:100%;height:100%;object-fit:cover;display:block;" onerror="this.style.display=\'none\'">'
      : '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>';
    var imgLabel = res.has_image ? 'Lot image analyzed' : (pageImg ? 'Catalog page' : 'No image available');'''

if old_img in content:
    content = content.replace(old_img, new_img)
    print('✅ image fixed')
else:
    print('❌ image not found')

# 2. Make comp rows clickable eBay links
old_comp = "      return '<div class=\"comp-row\"><div class=\"comp-title\">' + esc(c.title||'') + '</div><div class=\"comp-price\">' + (c.price ? '$' + parseInt(c.price).toLocaleString() : 'N/A') + '</div><div class=\"comp-date\">' + esc(c.date||'') + '</div><div class=\"comp-src\">' + esc(c.source||'eBay') + '</div></div>';"
new_comp = "      var ebaySearch = 'https://www.ebay.com/sch/i.html?_nkw=' + encodeURIComponent(c.title||'') + '&LH_Sold=1&LH_Complete=1';\n      return '<div class=\"comp-row\" style=\"cursor:pointer\" onclick=\"window.open(\\'' + ebaySearch + '\\',\\'_blank\\',\\'noopener,width=1200,height=800\\')\"><div class=\"comp-title\">' + esc(c.title||'') + '</div><div class=\"comp-price\">' + (c.price ? '$' + parseInt(c.price).toLocaleString() : 'N/A') + '</div><div class=\"comp-date\">' + esc(c.date||'') + '</div><div class=\"comp-src\">' + esc(c.source||'eBay') + '</div></div>';"

if old_comp in content:
    content = content.replace(old_comp, new_comp)
    print('✅ comp links fixed')
else:
    print('❌ comp links not found')

# 3. Fix Watch label - show notes as reason, hide if empty
old_rec = "        '<div class=\"rec-box ' + recClass + '\">' + recLabel + (res.rec_reason||res.notes ? ' \u2014 ' + esc(res.rec_reason||res.notes||'') : '') + '</div>' +"
new_rec = "        (res.rec_reason||res.notes ? '<div class=\"rec-box ' + recClass + '\">' + recLabel + ' \u2014 ' + esc(res.rec_reason||res.notes||'') + '</div>' : '') +"

if old_rec in content:
    content = content.replace(old_rec, new_rec)
    print('✅ watch label fixed')
else:
    print('❌ watch label not found')

open('templates/auction_research.html', 'w').write(content)
