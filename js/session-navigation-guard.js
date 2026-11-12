/* Navigation only. Do not revoke tokens or require registration on reload. */
(function(){
  'use strict';
  const path=(location.pathname.split('/').pop()||'').toLowerCase();
  let signedIn=false;
  try { signedIn=Boolean(localStorage.getItem('mathweb_token') || localStorage.getItem('mathweb_admin_token')); }catch(_){}
  // Server validation and expired-token handling are owned by auth.js.
  // A local-only redirect here traps users with stale tokens.
  function syncTrial(){
    document.querySelectorAll('#mathwebTrialBanner, .mathweb-trial-banner').forEach(el=>{
      el.hidden=signedIn;
      el.style.display=signedIn?'none':'';
    });
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',syncTrial,{once:true});else syncTrial();
  window.addEventListener('storage',syncTrial);
})();
