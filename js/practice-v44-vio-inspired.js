/* MATH_WEB V44: non-invasive question zoom controls.
   Does not alter questions, answers, timer, grading, or progress. */
(function(){
 'use strict';
 let zoom=100;
 const clamp=n=>Math.max(80,Math.min(140,n));
 function enhance(){
   const panel=document.querySelector('.mathweb-ai-panel');
   if(!panel || !panel.querySelector('#mathwebAiAnswerArea'))return;
   if(panel.querySelector('#v44-practice-tools'))return;
   const question=panel.querySelector('.mathweb-ai-question');
   if(!question)return;
   const tools=document.createElement('div');
   tools.id='v44-practice-tools';
   tools.setAttribute('aria-label','Điều chỉnh cỡ chữ câu hỏi');
   const minus=document.createElement('button'),plus=document.createElement('button'),out=document.createElement('output');
   minus.type=plus.type='button';minus.textContent='−';plus.textContent='+';
   minus.setAttribute('aria-label','Thu nhỏ chữ');plus.setAttribute('aria-label','Phóng to chữ');
   const update=()=>{out.textContent=zoom+'%';question.style.fontSize=`${zoom/100*20}px`;};
   minus.addEventListener('click',()=>{zoom=clamp(zoom-10);update()});
   plus.addEventListener('click',()=>{zoom=clamp(zoom+10);update()});
   tools.append(minus,out,plus);
   question.parentNode.insertBefore(tools,question);
   update();
 }
 const observer=new MutationObserver(enhance);
 function start(){observer.observe(document.body,{childList:true,subtree:true});enhance()}
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
