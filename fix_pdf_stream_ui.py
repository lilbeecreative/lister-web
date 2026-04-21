content = open('templates/index.html').read()

old_js = '''async function scanPdfAuction(input) {
  if (!input.files[0]) return;
  document.getElementById('pdf-scanning').style.display = '';
  document.getElementById('pdf-results').style.display = 'none';
  document.getElementById('pdf-drop-zone').style.display = 'none';

  // Animate progress bar
  const scanSteps = [
    {pct: 8,  label: 'Reading PDF...'},
    {pct: 20, label: 'Extracting lot data...'},
    {pct: 40, label: 'Sending to Gemini...'},
    {pct: 60, label: 'Researching item values...'},
    {pct: 75, label: 'Estimating market prices...'},
    {pct: 88, label: 'Finalizing results...'},
  ];
  let scanStep = 0;
  const scanInterval = setInterval(() => {
    if (scanStep < scanSteps.length) {
      const s = scanSteps[scanStep++];
      document.getElementById('pdf-scan-bar').style.width = s.pct + '%';
      document.getElementById('pdf-scan-pct').textContent = s.pct + '%';
      document.getElementById('pdf-scan-label').textContent = s.label;
    }
  }, 5000);

  try {
    const fd = new FormData();
    fd.append('file', input.files[0]);
    const r = await fetch('/api/auction/scan-pdf', {method: 'POST', body: fd});
    if (!r.ok) {
      const err = await r.json();
      clearInterval(scanInterval);
      toast('PDF scan failed: ' + (err.detail || 'Unknown error'), 'error');
      document.getElementById('pdf-scanning').style.display = 'none';
      document.getElementById('pdf-drop-zone').style.display = '';
      return;
    }
    // Get CSV
    const csvText = await r.text();
    pdfCsvBlob = new Blob([csvText], {type: 'text/csv'});

    // Parse CSV for display - proper quoted CSV parser
    function parseCSVLine(line) {
      const result = []; let cur = ''; let inQ = false;
      for (let i = 0; i < line.length; i++) {
        if (line[i] === '"') {
          if (inQ && line[i+1] === '"') { cur += '"'; i++; }
          else inQ = !inQ;
        } else if (line[i] === ',' && !inQ) { result.push(cur); cur = ''; }
        else cur += line[i];
      }
      result.push(cur);
      return result;
    }
    const lines = csvText.trim().split('\\n');
    const tbody = document.getElementById('pdf-result-body');
    tbody.innerHTML = '';
    lines.slice(1).forEach(line => {
      if (!line.trim()) return;
      const cols = parseCSVLine(line);
      if (!cols[1]) return;
      const val = parseFloat((cols[5]||'0').replace('$','').replace(/[^0-9.]/g,'')) || 0;
      const color = val > 100 ? 'pdf-value-high' : val > 0 ? 'pdf-value-low' : '';
      const link = cols[6] && cols[6].startsWith('http') ? `<a href="${cols[6]}" target="_blank" style="color:var(--accent);font-size:10px;">View</a>` : '';
      tbody.innerHTML += `<tr>
        <td style="color:var(--muted)">${cols[0]||''}</td>
        <td style="max-width:200px">${cols[1]||''}</td>
        <td>${cols[3]||''}</td>
        <td>${cols[4]||''}</td>
        <td class="${color}">${cols[5]||''}</td>
        <td>${link}</td>
      </tr>`;
    });

    clearInterval(scanInterval);
    document.getElementById('pdf-scan-bar').style.width = '100%';
    document.getElementById('pdf-scan-pct').textContent = '100%';
    document.getElementById('pdf-scan-label').textContent = 'Complete!';
    document.getElementById('pdf-result-title').textContent = `Results — ${lines.length-1} items`;
    setTimeout(() => {
      document.getElementById('pdf-scanning').style.display = 'none';
      document.getElementById('pdf-results').style.display = '';
    }, 500);
  } catch(e) {
    clearInterval(scanInterval);
    toast('PDF scan error: ' + e.message, 'error');
    document.getElementById('pdf-scanning').style.display = 'none';
    document.getElementById('pdf-drop-zone').style.display = '';
  }
  input.value = '';
}'''

new_js = '''let pdfAllItems = [];

async function scanPdfAuction(input) {
  if (!input.files[0]) return;
  pdfAllItems = [];
  document.getElementById('pdf-scanning').style.display = '';
  document.getElementById('pdf-results').style.display = '';
  document.getElementById('pdf-drop-zone').style.display = 'none';
  document.getElementById('pdf-result-body').innerHTML = '';
  document.getElementById('pdf-result-title').textContent = 'Scanning...';
  document.getElementById('pdf-scan-bar').style.width = '0%';
  document.getElementById('pdf-scan-pct').textContent = '0%';
  document.getElementById('pdf-scan-label').textContent = 'Uploading PDF...';

  try {
    const fd = new FormData();
    fd.append('file', input.files[0]);
    const r = await fetch('/api/auction/scan-pdf', {method: 'POST', body: fd});
    if (!r.ok) {
      const err = await r.json().catch(() => ({}));
      toast('PDF scan failed: ' + (err.detail || 'Unknown error'), 'error');
      document.getElementById('pdf-scanning').style.display = 'none';
      document.getElementById('pdf-drop-zone').style.display = '';
      return;
    }

    const reader = r.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, {stream: true});
      const lines = buffer.split('\\n');
      buffer = lines.pop();
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        try {
          const msg = JSON.parse(line.slice(6));
          if (msg.done) {
            document.getElementById('pdf-scan-bar').style.width = '100%';
            document.getElementById('pdf-scan-pct').textContent = '100%';
            document.getElementById('pdf-scan-label').textContent = 'Complete!';
            document.getElementById('pdf-result-title').textContent = `Results — ${pdfAllItems.length} items`;
            setTimeout(() => { document.getElementById('pdf-scanning').style.display = 'none'; }, 600);
            buildPdfCsv();
          } else {
            const pct = Math.round((msg.chunk / msg.total_chunks) * 95);
            document.getElementById('pdf-scan-bar').style.width = pct + '%';
            document.getElementById('pdf-scan-pct').textContent = pct + '%';
            document.getElementById('pdf-scan-label').textContent = `Section ${msg.chunk} of ${msg.total_chunks} — ${msg.items.length} items found`;
            document.getElementById('pdf-result-title').textContent = `Results — ${pdfAllItems.length + msg.items.length} items so far`;
            appendPdfItems(msg.items);
          }
        } catch(e) {}
      }
    }
  } catch(e) {
    toast('PDF scan error: ' + e.message, 'error');
    document.getElementById('pdf-scanning').style.display = 'none';
    document.getElementById('pdf-drop-zone').style.display = '';
  }
  input.value = '';
}

function appendPdfItems(items) {
  const tbody = document.getElementById('pdf-result-body');
  items.forEach(item => {
    pdfAllItems.push(item);
    const val = parseInt(item.your_value) || 0;
    const color = val > 100 ? 'pdf-value-high' : val > 0 ? 'pdf-value-low' : '';
    const ebayUrl = 'https://www.ebay.com/sch/i.html?_nkw=' + encodeURIComponent(item.title || '') + '&LH_Sold=1&LH_Complete=1';
    tbody.innerHTML += `<tr>
      <td style="color:var(--muted);white-space:nowrap">${item.lot||''}</td>
      <td style="max-width:200px"><a href="${ebayUrl}" target="_blank" style="color:var(--accent);font-weight:600;font-size:12px;">${item.title||''}</a></td>
      <td style="white-space:nowrap">$${item.estimate_low||0}</td>
      <td style="white-space:nowrap">$${item.estimate_high||0}</td>
      <td class="${color}" style="white-space:nowrap">$${item.your_value||0}</td>
      <td>${item.notes||''}</td>
    </tr>`;
  });
}

function buildPdfCsv() {
  const rows = [['Lot','Title','Description','Est. Low','Est. High','Your Value','Notes']];
  pdfAllItems.forEach(item => {
    rows.push([item.lot||'', item.title||'', item.description||'',
      '$'+(item.estimate_low||0), '$'+(item.estimate_high||0),
      '$'+(item.your_value||0), item.notes||'']);
  });
  const csv = rows.map(r => r.map(c => '"'+String(c).replace(/"/g,'""')+'"').join(',')).join('\\n');
  pdfCsvBlob = new Blob([csv], {type: 'text/csv'});
}'''

if old_js in content:
    content = content.replace(old_js, new_js)
    print('✅ JS updated to streaming')
else:
    print('❌ JS not found')

# Also update table headers to add Notes column
old_header = '<thead><tr><th>Lot</th><th>Title</th><th>Est. Low</th><th>Est. High</th><th>Your Value</th><th>Link</th></tr></thead>'
new_header = '<thead><tr><th>Lot</th><th>Title (click for eBay sold)</th><th>Est. Low</th><th>Est. High</th><th>Your Value</th><th>Notes</th></tr></thead>'
if old_header in content:
    content = content.replace(old_header, new_header)
    print('✅ Table header updated')

open('templates/index.html', 'w').write(content)
