content = open('templates/auction.html').read()

# 1. Fix the grid - the image is taking too much space and title overflows
# Current: 60px 80px 1fr 110px 44px 36px
# Fix to give image proper space and align headers
old_row_grid = 'grid-template-columns:60px 80px 1fr 110px 44px 36px;'
new_row_grid = 'grid-template-columns:64px 90px 1fr 100px 48px 32px;'
count = content.count(old_row_grid)
content = content.replace(old_row_grid, new_row_grid)
print(f'✅ grid replaced {count}x')

# 2. Fix image overflow in table - contain the image properly
old_thumb = '.thumb{width:72px;height:54px;border-radius:6px;object-fit:cover;cursor:pointer;border:1px solid #2d3348;background:#161b28;display:block;flex-shrink:0;}'
new_thumb = '.thumb{width:80px;height:60px;border-radius:6px;object-fit:cover;cursor:pointer;border:1px solid #2d3348;background:#161b28;display:block;flex-shrink:0;max-width:100%;}'
content = content.replace(old_thumb, new_thumb)

old_placeholder = '.thumb-placeholder{width:72px;height:54px;border-radius:6px;background:#161b28;border:1px solid #2d3348;display:flex;align-items:center;justify-content:center;flex-shrink:0;}'
new_placeholder = '.thumb-placeholder{width:80px;height:60px;border-radius:6px;background:#161b28;border:1px solid #2d3348;display:flex;align-items:center;justify-content:center;flex-shrink:0;}'
content = content.replace(old_placeholder, new_placeholder)

# 3. Fix item title overflow - prevent it from spilling
old_item_name = '.item-name{font-weight:600;color:#f1f5f9;line-height:1.4;cursor:pointer;font-size:14px;}'
new_item_name = '.item-name{font-weight:600;color:#f1f5f9;line-height:1.4;cursor:pointer;font-size:13px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}'
content = content.replace(old_item_name, new_item_name)

# 4. Fix row alignment - center items vertically
old_tbl_row = '.tbl-row{display:grid;grid-template-columns:64px 90px 1fr 100px 48px 32px;padding:14px 18px;border-bottom:1px solid #161b28;align-items:center;font-size:13px;gap:10px;transition:background .1s;}'
new_tbl_row = '.tbl-row{display:grid;grid-template-columns:64px 90px 1fr 100px 48px 32px;padding:12px 18px;border-bottom:1px solid #161b28;align-items:center;font-size:13px;gap:12px;transition:background .1s;min-height:80px;}'
content = content.replace(old_tbl_row, new_tbl_row)

open('templates/auction.html', 'w').write(content)
print('done')
