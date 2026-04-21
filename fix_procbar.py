content = open('templates/index.html').read()

old = '''function updateProcBar(stats) {
  var total = stats.total || 0;
  var proc = stats.processing || 0;
  var done = total - proc;
  var wrap = document.getElementById('proc-bar-wrap');
  if (!wrap) return;
  if (proc > 0 || done > 0) {
    wrap.style.display = '';
    var pct = total > 0 ? Math.round(done/total*100) : 0;
    document.getElementById('proc-bar-fill').style.width = pct + '%';
    document.getElementById('proc-bar-count').textContent = done + ' of ' + total + ' done';
    document.getElementById('proc-pill-done').textContent = done + ' complete';
    document.getElementById('proc-pill-scan').textContent = proc + ' scanning';
  } else {
    wrap.style.display = 'none';
  }
}'''

new = '''function updateProcBar(stats) {
  var scanned = stats.total || 0;
  var proc = stats.processing || 0;
  var grandTotal = scanned + proc;
  var wrap = document.getElementById('proc-bar-wrap');
  if (!wrap) return;
  if (proc > 0) {
    wrap.style.display = '';
    var pct = grandTotal > 0 ? Math.round(scanned/grandTotal*100) : 0;
    document.getElementById('proc-bar-fill').style.width = pct + '%';
    document.getElementById('proc-bar-count').textContent = scanned + ' of ' + grandTotal + ' done';
    document.getElementById('proc-pill-done').textContent = scanned + ' complete';
    document.getElementById('proc-pill-scan').textContent = proc + ' scanning';
  } else {
    wrap.style.display = 'none';
  }
}'''

if old in content:
    content = content.replace(old, new)
    open('templates/index.html', 'w').write(content)
    print('done')
else:
    print('not found')
