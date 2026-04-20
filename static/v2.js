var batchCond='new', itemCond='new', itemQty=1;
var pendingFiles=[], currentGroupId=null;
var sessionId=uid(), batchItems=[];
var uploading=false, dashTimer=null;

function uid(){return'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,function(c){var r=Math.random()*16|0,v=c=='x'?r:(r&0x3|0x8);return v.toString(16);});}
function show(id){var el=document.getElementById(id);if(el)el.classList.remove('hidden');}
function hide(id){var el=document.getElementById(id);if(el)el.classList.add('hidden');}
function esc(s){return(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}

document.getElementById('navScan').addEventListener('click',function(){switchView('scan');});
document.getElementById('navDashboard').addEventListener('click',function(){switchView('dashboard');});

function switchView(v){
  document.querySelectorAll('.view').forEach(function(e){e.classList.remove('active');});
  document.querySelectorAll('.nav-tab').forEach(function(e){e.classList.remove('active');});
  var vEl=document.getElementById(v+'View');if(vEl)vEl.classList.add('active');
  var nEl=document.getElementById('nav'+v.charAt(0).toUpperCase()+v.slice(1));if(nEl)nEl.classList.add('active');
  if(v==='dashboard'){loadDashboard();startDashPoll();}
}

document.getElementById('batchNew').addEventListener('click',function(){setBatchCond('new');});
document.getElementById('batchUsed').addEventListener('click',function(){setBatchCond('used');});
function setBatchCond(c){
  batchCond=c;
  document.getElementById('batchNew').classList.toggle('on',c==='new');
  document.getElementById('batchUsed').classList.toggle('on',c==='used');
  document.getElementById('batchHint').innerHTML='All items will be marked as <strong>'+c+'</strong>';
}

document.getElementById('startBatchBtn').addEventListener('click',startBatch);
async function startBatch(){
  sessionId=uid();batchItems=[];itemCond=batchCond;
  hide('startState');show('activeState');
  updateCondToggle();await createGroup();
}

async function createGroup(){
  pendingFiles=[];itemQty=1;
  document.getElementById('qtyVal').textContent='1';
  document.getElementById('photoStrip').innerHTML='';hide('photoStrip');
  document.getElementById('doneBtn').disabled=true;
  document.getElementById('doneBtn').textContent='Add photos to continue';
  document.getElementById('camBtn').classList.remove('has-files');
  document.getElementById('galBtn').classList.remove('has-files');
  document.getElementById('cameraInput').value='';
  document.getElementById('galleryInput').value='';
  document.getElementById('itemLabel').textContent='Item '+(batchItems.length+1);
  updateCondToggle();
  var r=await fetch('/api/groups',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session_id:sessionId,condition:itemCond})});
  var d=await r.json();currentGroupId=d.group_id||d.id;
}

document.getElementById('togNew').addEventListener('click',function(){setItemCond('new');});
document.getElementById('togUsed').addEventListener('click',function(){setItemCond('used');});
function setItemCond(c){itemCond=c;updateCondToggle();}
function updateCondToggle(){
  document.getElementById('togNew').className='tog'+(itemCond==='new'?' on-new':'');
  document.getElementById('togUsed').className='tog'+(itemCond==='used'?' on-used':'');
}

document.getElementById('qtyMinus').addEventListener('click',function(){changeQty(-1);});
document.getElementById('qtyPlus').addEventListener('click',function(){changeQty(1);});
function changeQty(d){itemQty=Math.max(1,itemQty+d);document.getElementById('qtyVal').textContent=itemQty;}

document.getElementById('cameraInput').addEventListener('change',function(){handleFiles(this,'cam');});
document.getElementById('galleryInput').addEventListener('change',function(){handleFiles(this,'gal');});

function handleFiles(input,src){
  if(!input.files.length)return;
  var files=Array.from(input.files).slice(0,10-pendingFiles.length);
  document.getElementById(src==='cam'?'camBtn':'galBtn').classList.add('has-files');
  var strip=document.getElementById('photoStrip');
  files.forEach(function(file){
    var thumb=document.createElement('div');thumb.className='photo-thumb';
    var img=document.createElement('img');img.src=URL.createObjectURL(file);
    var del=document.createElement('button');del.className='thumb-del';
    del.innerHTML='<svg width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';
    var idx=pendingFiles.length;
    del.addEventListener('click',function(){pendingFiles.splice(idx,1);thumb.remove();updateDoneBtn();});
    thumb.appendChild(img);thumb.appendChild(del);strip.appendChild(thumb);
    pendingFiles.push(file);
  });
  show('photoStrip');updateDoneBtn();input.value='';
}

function updateDoneBtn(){
  var btn=document.getElementById('doneBtn');
  btn.disabled=!pendingFiles.length;
  btn.textContent=pendingFiles.length?'Done — submit item':'Add photos to continue';
}

function compressImage(file){
  return new Promise(function(resolve){
    var canvas=document.createElement('canvas'),ctx=canvas.getContext('2d'),img=new Image(),url=URL.createObjectURL(file);
    img.onload=function(){
      var w=img.width,h=img.height,max=1600;
      if(w>max||h>max){if(w>h){h=Math.round(h*max/w);w=max;}else{w=Math.round(w*max/h);h=max;}}
      canvas.width=w;canvas.height=h;ctx.drawImage(img,0,0,w,h);URL.revokeObjectURL(url);
      canvas.toBlob(resolve,'image/jpeg',0.88);
    };img.src=url;
  });
}

document.getElementById('doneBtn').addEventListener('click',submitItem);
async function submitItem(){
  if(!pendingFiles.length||uploading)return;
  uploading=true;document.getElementById('doneBtn').disabled=true;show('uploadBadge');
  try{
    for(var i=0;i<pendingFiles.length;i++){
      document.getElementById('uploadText').textContent='Uploading photo '+(i+1)+' of '+pendingFiles.length+'...';
      var blob=await compressImage(pendingFiles[i]);
      var fd=new FormData();fd.append('file',blob,'photo_'+i+'.jpg');
      await fetch('/api/photos/upload?group_id='+currentGroupId,{method:'POST',body:fd});
    }
    document.getElementById('uploadText').textContent='Submitting...';
    await fetch('/api/groups/submit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({group_id:currentGroupId,condition:itemCond,quantity:itemQty})});
    batchItems.push({cond:itemCond,qty:itemQty,photos:pendingFiles.length,status:'scanning'});
    updateBatchStats();renderBatchList();show('batchListWrap');
  }catch(err){alert('Upload failed: '+err.message);}
  hide('uploadBadge');uploading=false;await createGroup();
}

function updateBatchStats(){
  document.getElementById('sc-scanned').textContent=batchItems.length;
  document.getElementById('sc-proc').textContent=batchItems.filter(function(i){return i.status==='scanning';}).length;
  document.getElementById('sc-done').textContent=batchItems.filter(function(i){return i.status==='done';}).length;
}

function renderBatchList(){
  document.getElementById('batchList').innerHTML=batchItems.slice().reverse().map(function(item){
    var st=item.status==='done'?'done':'scan';
    return '<div class="batch-item"><div class="bi-dot dot-'+st+'"></div><div class="bi-info"><div class="bi-title">'+item.photos+' photo'+(item.photos>1?'s':'')+' &middot; Qty '+item.qty+'</div><div class="bi-meta">'+item.cond+'</div></div><span class="bi-badge badge-'+st+'">'+(item.status==='done'?'Done':'Scanning')+'</span></div>';
  }).join('');
}

document.getElementById('endBatchBtn').addEventListener('click',endBatch);
async function endBatch(){
  currentGroupId=null;hide('activeState');show('completeState');
  document.getElementById('completeSub').textContent=batchItems.length+' item'+(batchItems.length!==1?'s':'')+' submitted';
  document.getElementById('completeList').innerHTML=batchItems.slice().reverse().map(function(item){
    return '<div class="batch-item"><div class="bi-dot dot-done"></div><div class="bi-info"><div class="bi-title">'+item.photos+' photo'+(item.photos>1?'s':'')+' &middot; Qty '+item.qty+'</div><div class="bi-meta">'+item.cond+'</div></div><span class="bi-badge badge-done">Submitted</span></div>';
  }).join('');
}

document.getElementById('newBatchBtn').addEventListener('click',function(){batchItems=[];sessionId=uid();hide('completeState');show('startState');});
document.getElementById('viewDashBtn').addEventListener('click',function(){switchView('dashboard');});

document.getElementById('quickBatchInput').addEventListener('change',handleQuickBatch);
async function handleQuickBatch(e){
  var files=Array.from(e.target.files);if(!files.length)return;
  hide('startState');show('quickBatchState');
  document.getElementById('qbProgress').textContent='0 / '+files.length;
  document.getElementById('qbBar').style.width='0%';
  var list=document.getElementById('qbList');list.innerHTML='';
  var items=files.map(function(f,i){
    var el=document.createElement('div');el.className='batch-item';
    el.innerHTML='<div class="bi-dot dot-queue"></div><div class="bi-info"><div class="bi-title">Photo '+(i+1)+'</div><div class="bi-meta">'+batchCond+'</div></div><span class="bi-badge badge-queue">Queued</span>';
    list.appendChild(el);return el;
  });
  for(var i=0;i<files.length;i++){
    items[i].innerHTML='<div class="bi-dot dot-scan"></div><div class="bi-info"><div class="bi-title">Photo '+(i+1)+'</div><div class="bi-meta">'+batchCond+'</div></div><span class="bi-badge badge-scan">Uploading</span>';
    try{
      var r=await fetch('/api/groups',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session_id:uid(),condition:batchCond})});
      var gd=await r.json();var gid=gd.group_id||gd.id;
      var blob=await compressImage(files[i]);
      var fd=new FormData();fd.append('file',blob,'photo_0.jpg');
      await fetch('/api/photos/upload?group_id='+gid,{method:'POST',body:fd});
      await fetch('/api/groups/submit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({group_id:gid,condition:batchCond,quantity:1})});
      items[i].innerHTML='<div class="bi-dot dot-done"></div><div class="bi-info"><div class="bi-title">Photo '+(i+1)+'</div><div class="bi-meta">'+batchCond+'</div></div><span class="bi-badge badge-done">Submitted</span>';
    }catch(err){
      items[i].innerHTML='<div class="bi-dot" style="background:#dc2626"></div><div class="bi-info"><div class="bi-title">Photo '+(i+1)+' failed</div></div><span class="bi-badge" style="background:#FEF2F2;color:#dc2626">Error</span>';
    }
    var pct=Math.round((i+1)/files.length*100);
    document.getElementById('qbBar').style.width=pct+'%';
    document.getElementById('qbProgress').textContent=(i+1)+' / '+files.length;
  }
}
document.getElementById('qbDoneBtn').addEventListener('click',function(){hide('quickBatchState');show('startState');switchView('dashboard');});

async function loadDashboard(){
  try{
    var sr=await fetch('/api/stats'),ir=await fetch('/api/listings');
    if(!sr.ok||!ir.ok)return;
    var stats=await sr.json(),data=await ir.json();
    var items=data.items||data||[];
    var total=stats.total||items.length||0;
    var proc=stats.processing||0;
    var val=stats.value||items.reduce(function(s,i){return s+parseFloat(i.price||0);},0);
    document.getElementById('d-total').textContent=total;
    document.getElementById('d-proc').textContent=proc;
    document.getElementById('d-value').textContent='$'+Math.round(val).toLocaleString();
    var done=total-proc;
    var pct=total>0?Math.round(done/total*100):0;
    document.getElementById('progBar').style.width=pct+'%';
    document.getElementById('procCount').textContent=done+' of '+total+' done';
    document.getElementById('pillDone').textContent=done+' complete';
    document.getElementById('pillScan').textContent=proc+' scanning';
    document.getElementById('pillQueue').textContent='0 queued';
    renderItems(items);
  }catch(e){console.error('dashboard error:',e);}
}

function startDashPoll(){if(dashTimer)clearInterval(dashTimer);dashTimer=setInterval(loadDashboard,8000);}

document.getElementById('downloadCsvBtn').addEventListener('click',function(){var a=document.createElement('a');a.href='/api/export/csv';a.download='';document.body.appendChild(a);a.click();document.body.removeChild(a);});
document.getElementById('newBatchFromDashBtn').addEventListener('click',function(){switchView('scan');});
document.getElementById('clearAllBtn').addEventListener('click',function(){show('clearBanner');});
document.getElementById('cancelClearBtn').addEventListener('click',function(){hide('clearBanner');});
document.getElementById('confirmClearBtn').addEventListener('click',async function(){
  hide('clearBanner');
  await fetch('/api/listings/archive-batch',{method:'POST'});
  loadDashboard();
});

function renderItems(items){
  var grid=document.getElementById('itemsGrid');
  if(!items.length){grid.innerHTML='<div class="empty-state">No items yet — start a batch scan.</div>';return;}
  var html='';
  items.forEach(function(item){
    var cond=item.condition||'new';
    var price=parseFloat(item.price||0).toFixed(2);
    var pid=item.photo_id||'';
    var photoUrl=item.thumb_url||item.photo_url||(pid?('/api/photo/'+pid):'');
    var photoHtml=photoUrl?'<img src="'+esc(photoUrl)+'" alt="" loading="lazy">':'<div class="no-photo"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1"><path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/></svg></div>';
    var gUrl='https://www.google.com/search?q='+encodeURIComponent(item.title||'');
    var eUrl='https://www.ebay.com/sch/i.html?_nkw='+encodeURIComponent(item.title||'')+'&LH_Sold=1&LH_Complete=1';
    html+='<div class="item-card" id="ic-'+item.id+'">'+
      '<div class="item-photo">'+photoHtml+
      '<span class="ic-cond '+cond+'">'+cond+'</span>'+
      '<button class="ic-del" data-id="'+item.id+'"><svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>'+
      '</div>'+
      '<div class="item-body">'+
      '<div><div class="field-lbl">Title</div><input class="title-input" type="text" value="'+esc(item.title||'')+'" data-id="'+item.id+'" data-field="title"></div>'+
      '<div class="search-btns">'+
      '<button class="search-btn" data-url="'+gUrl+'" data-target="_blank">Search Google</button>'+
      '<button class="search-btn" data-url="'+eUrl+'" data-target="_blank">eBay sold</button>'+
      '</div>'+
      '<div class="field-row">'+
      '<div class="price-wrap"><div class="field-lbl">Price</div><input class="price-input" type="number" step="0.01" value="'+price+'" data-id="'+item.id+'" data-field="price"></div>'+
      '<div class="cond-wrap"><div class="field-lbl">Condition</div><div class="item-cond-toggle">'+
      '<div class="ic-tog '+(cond==='new'?'on-new':'')+'" data-id="'+item.id+'" data-cond="new">New</div>'+
      '<div class="ic-tog '+(cond==='used'?'on-used':'')+'" data-id="'+item.id+'" data-cond="used">Used</div>'+
      '</div></div>'+
      '</div>'+
      '</div></div>';
  });
  grid.innerHTML=html;

  grid.querySelectorAll('.ic-del').forEach(function(btn){
    btn.addEventListener('click',function(){
      var id=this.getAttribute('data-id');
      var card=document.getElementById('ic-'+id);if(card)card.remove();
      fetch('/api/listings/'+id,{method:'DELETE'}).catch(function(){});
      loadDashboard();
    });
  });

  grid.querySelectorAll('.title-input').forEach(function(inp){
    inp.addEventListener('blur',function(){saveField(this.getAttribute('data-id'),this.getAttribute('data-field'),this.value);});
    inp.addEventListener('keydown',function(e){if(e.key==='Enter')this.blur();});
  });

  grid.querySelectorAll('.price-input').forEach(function(inp){
    inp.addEventListener('blur',function(){saveField(this.getAttribute('data-id'),this.getAttribute('data-field'),parseFloat(this.value));});
    inp.addEventListener('keydown',function(e){if(e.key==='Enter')this.blur();});
  });

  grid.querySelectorAll('.ic-tog').forEach(function(tog){
    tog.addEventListener('click',function(){
      var id=this.getAttribute('data-id');
      var cond=this.getAttribute('data-cond');
      var parent=this.parentElement;
      parent.querySelectorAll('.ic-tog').forEach(function(t){t.className='ic-tog';});
      this.className='ic-tog on-'+cond;
      var badge=document.querySelector('#ic-'+id+' .ic-cond');
      if(badge){badge.className='ic-cond '+cond;badge.textContent=cond;}
      saveField(id,'condition',cond);
    });
  });

  grid.querySelectorAll('.search-btn').forEach(function(btn){
    btn.addEventListener('click',function(){
      window.open(this.getAttribute('data-url'),'_blank','noopener');
    });
  });
}

async function saveField(id,field,value){
  try{await fetch('/api/listings/'+id,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({field:field,value:value})});}
  catch(e){console.error(e);}
}

setBatchCond('new');
loadDashboard();
