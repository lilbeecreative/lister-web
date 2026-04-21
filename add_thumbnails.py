content = open('templates/auction.html').read()

# 1. Add CSS for thumbnail and modal
old_css = '.empty-state{text-align:center;padding:60px 20px;color:#475569;font-size:14px;}'
new_css = '''.empty-state{text-align:center;padding:60px 20px;color:#475569;font-size:14px;}
.thumb{width:52px;height:40px;border-radius:6px;object-fit:cover;cursor:pointer;border:1px solid #2d3348;background:#161b28;display:block;}
.thumb:hover{border-color:#854F0B;transform:scale(1.05);}
.thumb-placeholder{width:52px;height:40px;border-radius:6px;background:#161b28;border:1px solid #2d3348;display:flex;align-items:center;justify-content:center;}
.img-modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:100;align-items:center;justify-content:center;padding:20px;}
.img-modal.open{display:flex;}
.img-modal-inner{position:relative;max-width:90vw;max-height:90vh;}
.img-modal img{max-width:85vw;max-height:85vh;border-radius:10px;object-fit:contain;display:block;}
.img-modal-close{position:absolute;top:-14px;right:-14px;width:30px;height:30px;border-radius:50%;background:#2d3348;border:none;color:#f1f5f9;cursor:pointer;font-size:16px;display:flex;align-items:center;justify-content:center;}'''
content = content.replace(old_css, new_css)
print('✅ CSS added' if old_css in open('templates/auction.html').read() else '✅ CSS added (already replaced)')

# 2. Add modal HTML before closing body
old_body_end = '</body>\n</html>'
new_body_end = '''<div class="img-modal" id="img-modal" onclick="closeModal()">
  <div class="img-modal-inner" onclick="event.stopPropagation()">
    <button class="img-modal-close" onclick="closeModal()">✕</button>
    <img id="img-modal-src" src="" alt="">
  </div>
</div>
</body>
</html>'''
content = content.replace(old_body_end, new_body_end)

# 3. Add modal functions to JS
old_js_end = "function esc(s){"
new_js_end = """function openImgModal(url) {
  document.getElementById('img-modal-src').src = url;
  document.getElementById('img-modal').classList.add('open');
}
function closeModal() {
  document.getElementById('img-modal').classList.remove('open');
  document.getElementById('img-modal-src').src = '';
}
document.addEventListener('keydown', function(e){ if(e.key==='Escape') closeModal(); });

function esc(s){"""
content = content.replace(old_js_end, new_js_end)

# 4. Update table grid to include thumbnail column
old_grid = "grid-template-columns:32px 60px 1fr 120px 50px 40px;"
new_grid = "grid-template-columns:32px 60px 62px 1fr 120px 50px 40px;"
content = content.replace(old_grid, new_grid)

# 5. Add "Image" header to table
old_tbl_head = '<div>Lot</div>\n        <div>Item</div>'
new_tbl_head = '<div>Lot</div>\n        <div></div>\n        <div>Item</div>'
content = content.replace(old_tbl_head, new_tbl_head)

# 6. Add thumbnail to each row in renderItems
old_row = """      '<input type="checkbox" class="chk" onchange="toggleSelect(\\'' + item._id + '\\',this.checked)" ' + (item._sel ? 'checked' : '') + '>' +
      '<div class="lot">#' + esc(item.lot||'') + '</div>' +"""
new_row = """      '<input type="checkbox" class="chk" onchange="toggleSelect(\\'' + item._id + '\\',this.checked)" ' + (item._sel ? 'checked' : '') + '>' +
      '<div class="lot">#' + esc(item.lot||'') + '</div>' +
      (item._page_img ? '<div><img class="thumb" src="' + esc(item._page_img) + '" onclick="openImgModal(\\'' + esc(item._page_img) + '\\')"></div>' : '<div><div class="thumb-placeholder"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#475569" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg></div></div>') +"""
content = content.replace(old_row, new_row)

open('templates/auction.html', 'w').write(content)
print('done')
