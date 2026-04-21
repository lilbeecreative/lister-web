content = open('templates/auction_research.html').read()

old_export = '''function exportResults() {
  var rows = [['Lot','Title','Original Value','Revised Value','Confidence','Recommendation','Comparable Sales','Image Notes']];
  watchItems.forEach(function(item) {
    var res = results[item.lot];
    var compsText = res && res.comps ? res.comps.map(function(c){return c.title+' $'+c.price+' ('+c.date+')'}).join('; ') : '';
    rows.push([
      item.lot||'', item.title||'',
      '$'+(item.your_value||0), res?'$'+(res.revised_value||0):'',
      res?res.confidence:'', res?res.recommendation:'',
      compsText, res?res.image_notes||'':''
    ]);
  });
  var csv = rows.map(function(r){return r.map(function(c){return '"'+String(c).replace(/"/g,'""')+'"';}).join(',');}).join('\\n');
  var a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([csv],{type:'text/csv'}));
  a.download = 'deep_research.csv';
  a.click();
}'''

new_export = '''async function exportResults() {
  var fd = new FormData();
  var exportData = watchItems.map(function(item) {
    var res = results[item.lot] || {};
    var cleanTitle = (item.title||'').replace(/\\s*,?\\s*QTY\\s*\\(?\\d*\\)?/gi,'').replace(/\\s*,?\\s*\\(\\d+\\)/g,'').replace(/,\\s*$/,'').trim();
    var ebayUrl = 'https://www.ebay.com/sch/i.html?_nkw=' + encodeURIComponent(cleanTitle) + '&LH_Sold=1&LH_Complete=1';
    return {
      lot: item.lot||'',
      title: item.title||'',
      original_value: item.your_value||0,
      revised_value: res.revised_value||0,
      confidence: res.confidence||'',
      recommendation: res.recommendation||'',
      rec_reason: res.rec_reason||res.notes||'',
      image_notes: res.image_notes||'',
      ebay_search: ebayUrl
    };
  });
  fd.append('items', JSON.stringify(exportData));
  try {
    var r = await fetch('/api/auction/research-export', {method:'POST', body:fd});
    if (!r.ok) { alert('Export failed'); return; }
    var blob = await r.blob();
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'deep_research.xlsx';
    a.click();
  } catch(e) {
    alert('Export error: ' + e.message);
  }
}'''

if old_export in content:
    content = content.replace(old_export, new_export)
    open('templates/auction_research.html', 'w').write(content)
    print('done')
else:
    print('not found')
