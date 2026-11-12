/* V27: restore working notification UI, keep header in normal document flow. */
(()=>{'use strict';
const page=(location.pathname.split('/').pop()||'index.html').toLowerCase();
if(page==='admin.html')return;
function setup(){
 if(page==='battle.html')document.body.classList.add('mw-v27-battle');
 const header=document.getElementById('mw-v5-header');if(!header)return;
 const actions=header.querySelector('.mw-v5-actions');if(!actions)return;
 const outdated=actions.querySelector('.mw-v5-icon');if(outdated)outdated.remove();
 const oldButton=document.getElementById('notificationButton');
 if(oldButton)oldButton.id='mw-v27-legacy-notification-button';
 const control=document.createElement('div');control.id='mw-v27-notification';
 const button=document.createElement('button');button.id='notificationButton';button.type='button';button.className='notification-button';button.setAttribute('aria-label','Mở thông báo');button.setAttribute('aria-expanded','false');button.setAttribute('aria-controls','notificationPanel');button.textContent='🔔';
 let badge=document.getElementById('notificationBadge');if(!badge){badge=document.createElement('span');badge.id='notificationBadge';badge.className='notification-badge'}button.append(badge);
 control.append(button);actions.prepend(control);
 let panel=document.getElementById('notificationPanel');
 if(!panel){
  panel=document.createElement('div');panel.id='notificationPanel';panel.className='notification-panel';
  const panelHead=document.createElement('div');panelHead.className='notification-header';
  const label=document.createElement('strong');label.className='notification-title';label.textContent='Thông báo';
  const read=document.createElement('button');read.type='button';read.id='readAllNotifications';read.className='notification-read-all';read.textContent='Đánh dấu đã đọc';
  const list=document.createElement('div');list.id='notificationList';list.className='notification-list';
  panelHead.append(label,read);panel.append(panelHead,list);
 }
 // Legacy navbar is hidden by NEON; reparent to body so its fixed panel is accessible.
 panel.classList.add('mw-v27-panel');document.body.append(panel);
 if(window.MATHWEB_NOTIFICATIONS){button.dataset.notificationBound='true';button.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();window.MATHWEB_NOTIFICATIONS.openNotifications()})}
 if(!document.querySelector('link[href*="notification.css"]')){
  const css=document.createElement('link');css.rel='stylesheet';css.href='css/notification.css';document.head.append(css);
 }
 if(!document.querySelector('script[src*="notification.js"]')){
  const script=document.createElement('script');script.src='js/notification.js';document.body.append(script);
 }
 // When notification.js already loaded, the DOMContentLoaded handler can now see the new button.
 // For async scripts, notification.js runs its own initializer.
 // The header is NOT sticky: it scrolls naturally out of view and returns at page top.
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup,{once:true});else setup();
})();
