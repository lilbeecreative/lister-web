content = open('templates/auction_research.html').read()

# Replace comp rows to just open eBay sold search with the item title
old_comp = "      var ebaySearch = 'https://www.ebay.com/sch/i.html?_nkw=' + encodeURIComponent(c.title||'') + '&LH_Sold=1&LH_Complete=1';\n      return '<div class=\"comp-row\" style=\"cursor:pointer\" onclick=\"window.open(\\'' + ebaySearch + '\\',\\'_blank\\',\\'noopener,width=1200,height=800\\')\"><div class=\"comp-title\">' + esc(c.title||'') + '</div><div class=\"comp-price\">' + (c.price ? '$' + parseInt(c.price).toLocaleString() : 'N/A') + '</div><div class=\"comp-date\">' + esc(c.date||'') + '</div><div class=\"comp-src\">' + esc(c.source||'eBay') + '</div></div>';"

new_comp = "      var itemTitle = item.title || '';\n      var ebaySearch = 'https://www.ebay.com/sch/i.html?_nkw=' + encodeURIComponent(itemTitle) + '&LH_Sold=1&LH_Complete=1';\n      return '<div class=\"comp-row\" style=\"cursor:pointer\" onclick=\"window.open(\\'' + ebaySearch + '\\',\\'_blank\\',\\'noopener,width=1200,height=800\\')\"><div class=\"comp-title\">' + esc(c.title||'') + '</div><div class=\"comp-price\">' + (c.price ? '$' + parseInt(c.price).toLocaleString() : 'N/A') + '</div><div class=\"comp-date\">' + esc(c.date||'') + '</div><div class=\"comp-src\">eBay Sold ↗</div></div>';"

if old_comp in content:
    content = content.replace(old_comp, new_comp)
    print('✅ comp links updated')
else:
    print('❌ not found')

open('templates/auction_research.html', 'w').write(content)
