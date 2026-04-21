content = open('templates/index.html').read()

# Add CSS
old_css = '.nav-btn[data-tab="auction"].active { background: var(--amber); }'
new_css = '''.nav-btn[data-tab="auction"].active { background: var(--amber); }
.pdf-drop-zone { border: 2px dashed var(--border); border-radius: 12px; padding: 28px; text-align: center; cursor: pointer; transition: border-color 0.15s; position: relative; overflow: hidden; margin-bottom: 14px; }
.pdf-drop-zone:hover { border-color: var(--amber); }
.pdf-drop-zone input { position: absolute; inset: 0; opacity: 0; cursor: pointer; width: 100%; height: 100%; }
.pdf-result-table { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 12px; }
.pdf-result-table th { background: var(--surface); color: var(--muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; font-size: 10px; padding: 8px 10px; text-align: left; border-bottom: 1px solid var(--border); }
.pdf-result-table td { padding: 8px 10px; border-bottom: 1px solid var(--border); color: var(--text); vertical-align: top; }
.pdf-result-table tr:hover td { background: var(--surface); }
.pdf-value-high { color: #4ade80; font-weight: 700; }
.pdf-value-low { color: #f59e0b; font-weight: 700; }'''

if old_css in content:
    content = content.replace(old_css, new_css)
    print('✅ CSS added')
else:
    print('❌ CSS not found')

# Add PDF section to auction tab
old_auction = '''  <div class="tab-content" id="tab-auction">
    <div style="display:flex;gap:8px;align-items:center;margin-bottom:10px;flex-wrap:wrap;">'''

new_auction = '''  <div class="tab-content" id="tab-auction">
    <!-- PDF Auction Scanner -->
    <div style="margin-bottom:20px;">
      <div style="font-size:14px;font-weight:700;color:var(--text);margin-bottom:10px;">📄 PDF Auction Scanner</div>
      <div class="pdf-drop-zone" id="pdf-drop-zone">
        <input type="file" id="pdf-input" accept=".pdf" onchange="scanPdfAuction(this)">
        <div style="font-size:2rem;margin-bottom:8px;">📄</div>
        <div style="font-size:14px;font-weight:700;color:var(--text);margin-bottom:4px;">Upload auction PDF</div>
        <div style="font-size:12px;color:var(--muted);">Gemini will extract all items and estimate values</div>
      </div>
      <div id="pdf-scanning" style="display:none;background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:14px;text-align:center;margin-bottom:14px;">
        <div style="font-size:13px;color:var(--amber);font-weight:600;">⏳ Scanning PDF with Gemini...</div>
        <div style="font-size:11px;color:var(--muted);margin-top:4px;">This may take 30-60 seconds</div>
      </div>
      <div id="pdf-results" style="display:none;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <div style="font-size:13px;font-weight:700;color:var(--text);" id="pdf-result-title">Results</div>
          <button class="btn" style="font-size:11px;padding:4px 12px;" onclick="downloadPdfCsv()">⬇️ Download CSV</button>
        </div>
        <div style="overflow-x:auto;">
          <table class="pdf-result-table" id="pdf-result-table">
            <thead><tr><th>Lot</th><th>Title</th><th>Est. Low</th><th>Est. High</th><th>Your Value</th><th>Link</th></tr></thead>
            <tbody id="pdf-result-body"></tbody>
          </table>
        </div>
      </div>
    </div>
    <div style="border-top:1px solid var(--border);padding-top:16px;margin-bottom:10px;font-size:14px;font-weight:700;color:var(--text);">🔗 URL Scanner</div>
    <div style="display:flex;gap:8px;align-items:center;margin-bottom:10px;flex-wrap:wrap;">'''

if old_auction in content:
    content = content.replace(old_auction, new_auction)
    print('✅ Auction UI added')
else:
    print('❌ Auction tab not found')

# Add JS
old_js = '// ── FAST SCAN ─────────────────────────────────────────────────'
new_js = '''// ── PDF AUCTION SCAN ──────────────────────────────────────────
let pdfCsvBlob = null;

async function scanPdfAuction(input) {
  if (!input.files[0]) return;
  document.getElementById('pdf-scanning').style.display = '';
  document.getElementById('pdf-results').style.display = 'none';
  document.getElementById('pdf-drop-zone').style.display = 'none';

  try {
    const fd = new FormData();
    fd.append('file', input.files[0]);
    const r = await fetch('/api/auction/scan-pdf', {method: 'POST', body: fd});
    if (!r.ok) {
      const err = await r.json();
      toast('PDF scan failed: ' + (err.detail || 'Unknown error'), 'error');
      document.getElementById('pdf-scanning').style.display = 'none';
      document.getElementById('pdf-drop-zone').style.display = '';
      return;
    }
    // Get CSV
    const csvText = await r.text();
    pdfCsvBlob = new Blob([csvText], {type: 'text/csv'});

    // Parse CSV for display
    const lines = csvText.trim().split('\\n');
    const tbody = document.getElementById('pdf-result-body');
    tbody.innerHTML = '';
    lines.slice(1).forEach(line => {
      const cols = line.split(',').map(c => c.replace(/^"|"$/g,'').replace(/""/g,'"'));
      if (!cols[1]) return;
      const val = parseFloat((cols[5]||'0').replace('$','')) || 0;
      const color = val > 100 ? 'pdf-value-high' : val > 0 ? 'pdf-value-low' : '';
      const link = cols[6] ? `<a href="${cols[6]}" target="_blank" style="color:var(--accent);font-size:10px;">View</a>` : '';
      tbody.innerHTML += `<tr>
        <td style="color:var(--muted)">${cols[0]}</td>
        <td style="max-width:200px">${cols[1]}</td>
        <td>${cols[3]||''}</td>
        <td>${cols[4]||''}</td>
        <td class="${color}">${cols[5]||''}</td>
        <td>${link}</td>
      </tr>`;
    });

    document.getElementById('pdf-result-title').textContent = `Results — ${lines.length-1} items`;
    document.getElementById('pdf-scanning').style.display = 'none';
    document.getElementById('pdf-results').style.display = '';
  } catch(e) {
    toast('PDF scan error: ' + e.message, 'error');
    document.getElementById('pdf-scanning').style.display = 'none';
    document.getElementById('pdf-drop-zone').style.display = '';
  }
  input.value = '';
}

function downloadPdfCsv() {
  if (!pdfCsvBlob) return;
  const a = document.createElement('a');
  a.href = URL.createObjectURL(pdfCsvBlob);
  a.download = 'auction_scan.csv';
  a.click();
}

// ── FAST SCAN ─────────────────────────────────────────────────'''

if old_js in content:
    content = content.replace(old_js, new_js)
    print('✅ JS added')
else:
    print('❌ JS anchor not found')

open('templates/index.html', 'w').write(content)
