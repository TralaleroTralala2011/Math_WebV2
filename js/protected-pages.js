/* MATH_WEB: protected pages, client-side navigation gate. Server APIs must also verify tokens. */
(()=>{'use strict';
 const page=(location.pathname.split('/').pop()||'index.html').toLowerCase();
 const protectedPages=new Set(['practise.html','practice.html','learning-path.html','account.html','battle.html','chat.html','friends.html','assignments.html']);
 if(!protectedPages.has(page))return;
 const token=localStorage.getItem('mathweb_token');
 if(!token||!token.trim()){
   const next=encodeURIComponent(page+location.search);
   location.replace('login.html?next='+next);
 }
})();
