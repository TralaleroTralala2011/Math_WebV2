/* MATH_WEB V43: non-destructive logout confirmation. */
(function(){
  'use strict';
  let openPromise=null;
  window.mathwebConfirmLogout=function(){
    if(openPromise)return openPromise;
    openPromise=new Promise(resolve=>{
      const layer=document.createElement('div');layer.className='mw-logout-overlay';
      layer.setAttribute('role','presentation');
      layer.innerHTML='<section class="mw-logout-dialog" role="alertdialog" aria-modal="true" aria-labelledby="mw-logout-title" aria-describedby="mw-logout-desc" tabindex="-1"><span class="mw-logout-icon" aria-hidden="true">🔐</span><h2 id="mw-logout-title">Xác nhận đăng xuất?</h2><p id="mw-logout-desc">Bạn có chắc muốn đăng xuất khỏi MATH_WEB? Nếu chọn Ở lại, tài khoản và phiên đăng nhập sẽ được giữ nguyên.</p><div class="mw-logout-actions"><button type="button" data-mw-logout="cancel">Ở lại</button><button type="button" data-mw-logout="confirm">Đăng xuất</button></div></section>';
      let previous=document.activeElement;
      const cancel=layer.querySelector('[data-mw-logout="cancel"]');
      const confirm=layer.querySelector('[data-mw-logout="confirm"]');
      function finish(ok){document.removeEventListener('keydown',onKey,true);layer.remove();openPromise=null;if(previous&&previous.isConnected&&previous.focus)previous.focus();resolve(ok);}
      function onKey(e){if(e.key==='Escape'){e.preventDefault();finish(false);}else if(e.key==='Tab'){const active=document.activeElement;if(e.shiftKey&&active===cancel){e.preventDefault();confirm.focus();}else if(!e.shiftKey&&active===confirm){e.preventDefault();cancel.focus();}}}
      cancel.addEventListener('click',()=>finish(false));confirm.addEventListener('click',()=>finish(true));
      layer.addEventListener('click',e=>{if(e.target===layer)finish(false)});
      document.body.appendChild(layer);document.addEventListener('keydown',onKey,true);cancel.focus();
    });
    return openPromise;
  };
})();
