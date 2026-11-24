(()=>{'use strict';
if(document.body.classList.contains('standalone-preview')&&location.protocol==='file:')document.querySelector('.demo-logo')?.setAttribute('href','../../index.html');
const button=document.getElementById('mobile-menu-btn'),menu=document.getElementById('mobile-menu');
const closeMenu=()=>{if(!menu||!button)return;menu.hidden=true;button.setAttribute('aria-expanded','false');button.setAttribute('aria-label','Open navigation');};
if(button&&menu){button.addEventListener('click',()=>{const open=button.getAttribute('aria-expanded')==='true';menu.hidden=open;button.setAttribute('aria-expanded',String(!open));button.setAttribute('aria-label',open?'Open navigation':'Close navigation');});menu.querySelectorAll('a').forEach(a=>a.addEventListener('click',closeMenu));document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!menu.hidden){closeMenu();button.focus();}});matchMedia('(min-width:1001px)').addEventListener('change',closeMenu);}
const account=document.getElementById('account-dialog');if(account)document.querySelectorAll('a[href^="#account-"]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();account.showModal();}));
document.querySelectorAll('[data-close-dialog]').forEach(b=>b.addEventListener('click',()=>b.closest('dialog')?.close()));
document.querySelectorAll('dialog').forEach(d=>d.addEventListener('click',e=>{if(e.target!==d)return;const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close();}));
})();
