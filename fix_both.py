content = open('templates/auction.html').read()

# 1. Fix overlap - the image cell needs explicit width and the title cell needs to be a proper block
# The issue is the image isn't constraining its cell properly
old_thumb = '.thumb{width:80px;height:60px;border-radius:6px;object-fit:cover;cursor:pointer;border:1px solid #2d3348;background:#161b28;display:block;flex-shrink:0;max-width:100%;}'
new_thumb = '.thumb{width:86px;height:64px;border-radius:6px;object-fit:cover;cursor:pointer;border:1px solid #2d3348;background:#161b28;display:block;}'
content = content.replace(old_thumb, new_thumb)

# Force the image column div to be constrained
old_img_cell = "(item._page_img ? '<div><img class=\"thumb\" src=\"' + esc(item._page_img) + '\" onclick=\"openImgModal(\\'' + esc(item._page_img) + '\\')\"></div>' : '<div><div class=\"thumb-placeholder\"><svg"
new_img_cell = "(item._page_img ? '<div style=\"width:90px;flex-shrink:0\"><img class=\"thumb\" src=\"' + esc(item._page_img) + '\" onclick=\"openImgModal(\\'' + esc(item._page_img) + '\\')\" style=\"display:block;width:86px;height:64px;object-fit:cover;border-radius:6px;\"></div>' : '<div style=\"width:90px;flex-shrink:0\"><div class=\"thumb-placeholder\"><svg"

if old_img_cell in content:
    content = content.replace(old_img_cell, new_img_cell)
    print('✅ image cell fixed')
else:
    print('❌ image cell not found')

# 2. Fix search query - strip quantity/modifier text
old_ebay = "    var ebayUrl = 'https://www.ebay.com/sch/i.html?_nkw=' + encodeURIComponent(item.title || '') + '&LH_Sold=1&LH_Complete=1';"
new_ebay = """    // Strip quantity/modifier text for cleaner search
    var cleanTitle = (item.title||'').replace(/[,\\s]*\\(\\d+\\)[,\\s]*/g,'').replace(/\\bQTY\\s*\\(?\\d+\\)?/gi,'').replace(/\\bLOT OF \\d+/gi,'').replace(/\\bSET OF \\d+/gi,'').trim();
    var ebayUrl = 'https://www.ebay.com/sch/i.html?_nkw=' + encodeURIComponent(cleanTitle) + '&LH_Sold=1&LH_Complete=1';"""
if old_ebay in content:
    content = content.replace(old_ebay, new_ebay)
    print('✅ search query cleaned')
else:
    print('❌ ebayUrl not found')

open('templates/auction.html', 'w').write(content)
print('done')
