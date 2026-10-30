'use strict';
const $=id=>document.getElementById(id),cloud=window.csCloud;
const status=text=>{$('status').textContent=text;};
async function run(fn){try{await fn();}catch(e){status(e.message);}}
function state(){$('connect').hidden=cloud.connected();$('disconnect').hidden=!cloud.connected();}
async function refresh(){
 state();if(!cloud.connected()){status('Connect Cloud to see your documents here.');$('documents').replaceChildren();return;}
 status('Loading your documents…');await cloud.mkdir('/Documents');
 const files=(await cloud.list('/Documents')).filter(f=>!f.directory&&/\.(docx?|xlsx?|pptx?|odt|ods|odp|pdf|txt|rtf|csv)$/i.test(f.name)).sort((a,b)=>Date.parse(b.modified)-Date.parse(a.modified));
 $('documents').replaceChildren();
 for(const file of files){const li=document.createElement('li'),link=document.createElement('a'),date=document.createElement('small');link.href=cloud.editorUrl(file.id);link.textContent=file.name;const d=new Date(file.modified);date.textContent=isNaN(d)?'':d.toLocaleDateString();li.append(link,date);$('documents').append(li);}
 status(files.length?'Saved in your Cloud Documents folder.':'Your next document can start here.');
}
$('connect').onclick=()=>run(async()=>{await cloud.connect();await refresh();});
$('disconnect').onclick=()=>{cloud.disconnect();state();$('documents').replaceChildren();status('Disconnected on this device. Revoke this device password in Cloud’s security settings to end its access completely.');};
$('refresh').onclick=()=>run(refresh);
for(const b of document.querySelectorAll('[data-template]'))b.onclick=()=>run(async()=>{
 if(!cloud.connected()){status('Connect MNCloud first.');$('connect').focus();return;}
 const ext=b.dataset.template,dialog=$('name-dialog');$('name').value='Untitled';dialog.returnValue='cancel';dialog.showModal();$('name').select();
 const choice=await new Promise(resolve=>dialog.addEventListener('close',()=>resolve(dialog.returnValue),{once:true}));if(choice!=='ok')return;
 const name=$('name').value.trim();if(!name||/[\/\\\x00-\x1f]/.test(name)||name==='.'||name==='..')throw Error('Use a file name without slashes.');
 status('Creating your file…');const template=await fetch('/mn-office/templates/blank.'+ext);if(!template.ok)throw Error('The template could not be loaded.');
 await cloud.mkdir('/Documents');const path='/Documents/'+name.replace(new RegExp('\\.'+ext+'$','i'),'')+'.'+ext;
 await cloud.save(path,await template.blob());
 const file=(await cloud.list('/Documents')).find(f=>f.path===path);if(!file?.id)throw Error('Your document was created. Refresh the list to open it.');
 location.href=cloud.editorUrl(file.id);
});
try{document.documentElement.dataset.theme=localStorage.getItem('mn-theme')||'';}catch{}
$('theme').onclick=()=>{const e=document.documentElement;const dark=e.dataset.theme==='dark'||(!e.dataset.theme&&matchMedia('(prefers-color-scheme:dark)').matches);e.dataset.theme=dark?'light':'dark';try{localStorage.setItem('mn-theme',e.dataset.theme);}catch{}};
run(refresh);
