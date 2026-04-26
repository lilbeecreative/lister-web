content = open('templates/auction.html').read()

# Add CSS for the two action buttons
old_css = '.ico-btn{background:transparent;border:1px solid #2d3348;border-radius:6px;color:#64748b;cursor:pointer;font-size:13px;padding:4px 8px;}'
new_css = '''.ico-btn{background:transparent;border:1px solid #2d3348;border-radius:6px;color:#64748b;cursor:pointer;font-size:13px;padding:4px 8px;}
.ico-btn-ebay{background:#0f3460;border:1px solid #1a4a8a;border-radius:6px;color:#60a5fa;cursor:pointer;font-size:10px;font-weight:700;padding:4px 7px;white-space:nowrap;}
.ico-btn-ebay:hover{background:#1a4a8a;}
.ico-btn-gemini{background:#2d1f4e;border:1px solid #4c3580;border-radius:6px;color:#c084fc;cursor:pointer;font-size:10px;font-weight:700;padding:4px 7px;white-space:nowrap;}
.ico-btn-gemini:hover{background:#4c3580;}'''
if old_css in content:
    content = content.replace(old_css, new_css)
    print('✅ CSS added')
else:
    print('❌ ico-btn css not found')

# Update grid to fit two buttons
old_grid = 'grid-template-columns:64px 90px 1fr 100px 48px 32px;'
new_grid = 'grid-template-columns:64px 90px 1fr 100px 48px 60px 60px;'
content = content.replace(old_grid, new_grid)

# Update header too
old_head = '''          <div>Watch</div>
          <div></div>'''
new_head = '''          <div>Watch</div>
          <div></div>
          <div></div>'''
content = content.replace(old_head, new_head)

# Replace single arrow button with two buttons
old_btns = "'<button class=\"ico-btn\" onclick=\"window.open(\\'' + ebayUrl + '\\',\\'_blank\\',\\'noopener,width=1200,height=800\\'\" title=\"Search\">↗</button>' +"
new_btns = """'<button class=\"ico-btn-ebay\" onclick=\"window.open(\\'' + ebayUrl + '\\',\\'_blank\\',\\'noopener,width=1200,height=800\\')\">eBay</button>' +
      '<button class=\"ico-btn-gemini\" onclick=\"openGemini(\\'' + cleanTitle.replace(/\\'/g,\\'\\\\\\\\\\'\\')+\\'\\',\\'' + encodeURIComponent(item._page_img||\\'\\')+\\'\\')\">✨</button>' +"""
if old_btns in content:
    content = content.replace(old_btns, new_btns)
    print('✅ buttons replaced')
else:
    print('❌ buttons not found')

# Remove the search menu since we have two dedicated buttons now
# Keep the openSearchMenu but add openGemini function
old_js = "function openSearchMenu(e, title) {"
new_js = """function openGemini(title, imgUrl) {
  var prompt = 'I am evaluating this auction item for resale. Research and give me:\\n\\n' +
    'Item: ' + title + '\\n\\n' +
    '1. Current eBay sold prices for this exact item\\n' +
    '2. Typical resale value range\\n' +
    '3. Any key factors that affect value (condition, model variants, accessories)\\n' +
    '4. Buy recommendation (yes/no and why)';
  if (imgUrl) {
    prompt += '\\n\\nThe catalog image URL is: ' + decodeURIComponent(imgUrl);
  }
  window.open('https://gemini.google.com/app?q=' + encodeURIComponent(prompt), '_blank', 'noopener,width=1000,height=800');
}

function openSearchMenu(e, title) {"""
if old_js in content:
    content = content.replace(old_js, new_js)
    print('✅ openGemini added')
else:
    print('❌ openSearchMenu not found - adding openGemini before startUrlScan')
    content = content.replace('async function startUrlScan()', 
        'function openGemini(title, imgUrl) {\n  var prompt = \'I am evaluating this auction item for resale. Research and give me:\\\\n\\\\nItem: \' + title + \'\\\\n\\\\n1. Current eBay sold prices\\\\n2. Typical resale value range\\\\n3. Key value factors\\\\n4. Buy recommendation\';\n  window.open(\'https://gemini.google.com/app?q=\' + encodeURIComponent(prompt), \'_blank\', \'noopener,width=1000,height=800\');\n}\n\nasync function startUrlScan()')
    print('✅ openGemini added before startUrlScan')

open('templates/auction.html', 'w').write(content)
