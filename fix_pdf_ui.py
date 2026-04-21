content = open('templates/index.html').read()

# Fix CSV parser - replace naive split with proper quoted CSV parser
old_js = '''    // Parse CSV for display
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
    });'''

new_js = '''    // Parse CSV for display - proper quoted CSV parser
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
    });'''

if old_js in content:
    content = content.replace(old_js, new_js)
    print('✅ CSV parser fixed')
else:
    print('❌ not found')

open('templates/index.html', 'w').write(content)
