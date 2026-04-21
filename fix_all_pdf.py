import re

# Fix main.py
content = open('main.py').read()

# 1. Restore ScanAuction model
old = '@app.post("/api/auction/scan")\nasync def scan_auction(body: ScanAuction):'
new = 'class ScanAuction(BaseModel):\n    url: str\n\n@app.post("/api/auction/scan")\nasync def scan_auction(body: ScanAuction):'
if old in content and 'class ScanAuction' not in content:
    content = content.replace(old, new)
    print('✅ ScanAuction model restored')
else:
    print('ℹ️  ScanAuction already present or anchor not found')

open('main.py', 'w').write(content)

# Fix index.html
content = open('templates/index.html').read()

# 2. Fix scanning div - replace simple version with progress bar version
old_div = '''      <div id="pdf-scanning" style="display:none;background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:14px;text-align:center;margin-bottom:14px;">
        <div style="font-size:13px;color:var(--amber);font-weight:600;">⏳ Scanning PDF with Gemini...</div>
        <div style="font-size:11px;color:var(--muted);margin-top:4px;">This may take 30-60 seconds</div>
      </div>'''

new_div = '''      <div id="pdf-scanning" style="display:none;background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px;margin-bottom:14px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <div style="font-size:12px;font-weight:600;color:var(--amber);text-transform:uppercase;letter-spacing:0.06em;" id="pdf-scan-label">Reading PDF...</div>
          <div style="font-size:11px;color:var(--muted);" id="pdf-scan-pct">0%</div>
        </div>
        <div style="height:5px;background:var(--border);border-radius:3px;overflow:hidden;margin-bottom:10px;">
          <div id="pdf-scan-bar" style="height:100%;background:var(--amber);border-radius:3px;width:0%;transition:width 0.6s ease;"></div>
        </div>
        <div style="font-size:11px;color:var(--muted);text-align:center;">Items will appear below as each section completes</div>
      </div>'''

if old_div in content:
    content = content.replace(old_div, new_div)
    print('✅ Scanning div updated with progress bar')
else:
    # Check if already updated
    if 'pdf-scan-bar' in content:
        print('ℹ️  Progress bar already present')
    else:
        print('❌ Scanning div not found')

open('templates/index.html', 'w').write(content)
