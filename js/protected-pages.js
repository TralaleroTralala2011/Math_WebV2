/* MATH_WEB: protected pages, client-side navigation gate. Server APIs must also verify tokens. */
(()=>{'use strict';
 const segments=location.pathname.split('/').filter(Boolean);
 const page=(segments[segments.length-1]||'index.html').toLowerCase();
 const gameIndex=segments.lastIndexOf('games');
 const isGame=gameIndex>=0;
 const protectedPages=new Set(['practise.html','practice.html','learning-path.html','account.html','battle.html','chat.html','friends.html','assignments.html','learn.html','learning.html','geometry-studio.html','geometry-learning.html','geometry-lab.html','study-suite.html','curriculum-studio.html','learning-progress.html','final-features.html']);
 if(!protectedPages.has(page)&&!isGame)return;
 const token=localStorage.getItem('mathweb_token');
 if(!token||!token.trim()){
   const next=encodeURIComponent((isGame?segments.slice(gameIndex).join('/'):page)+location.search);
   // One ../ per segment inside games; works for both /games/topic/ and
   // /games/knowledge/topic/ without assuming the site's hosting base path.
   const rootPrefix=isGame?'../'.repeat(segments.length-gameIndex-1):'';
   location.replace(rootPrefix+'login.html?next='+next);
 }
})();
