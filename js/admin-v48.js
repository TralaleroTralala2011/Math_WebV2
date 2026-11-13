/* MATH_WEB V48 admin UX enhancement: preserve original handlers */
(()=>{'use strict';
 const ready=()=>{const app=document.getElementById('appView');if(!app)return;
 const actions=app.querySelector('.top-actions');if(actions&&!actions.querySelector('.v48-status')){const el=document.createElement('span');el.className='v48-status';el.textContent='Khu vực quản trị';actions.prepend(el)}
 const side=app.querySelector('.side');if(!side)return;
 side.addEventListener('click',e=>{const btn=e.target.closest('.navbtn');if(!btn)return;const page=document.getElementById('page-'+btn.dataset.page);if(!page)return;requestAnimationFrame(()=>{if(page.classList.contains('hidden'))return;page.classList.remove('v48-enter');void page.offsetWidth;page.classList.add('v48-enter')});if(window.matchMedia('(max-width:800px)').matches)btn.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion:reduce)').matches?'auto':'smooth',block:'nearest',inline:'center'});});
 side.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key))return;const buttons=[...side.querySelectorAll('.navbtn:not(:disabled)')];const i=buttons.indexOf(document.activeElement);if(i<0)return;e.preventDefault();const delta=['ArrowRight','ArrowDown'].includes(e.key)?1:-1;buttons[(i+delta+buttons.length)%buttons.length].focus()});
 };
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',ready,{once:true});else ready();
})();
