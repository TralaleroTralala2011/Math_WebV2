"use strict";
/* Only distribute verified existing types. Never fabricate a question type. */
window.MathWebQuestionMix={
 kind(q){const t=String(q?.type||q?.question_type||q?.format||'').toLowerCase();if(['true_false','true-false','boolean','dung_sai'].includes(t))return 'true_false';if(['short_answer','short-answer','fill','fill_in','essay','written','tu_luan'].includes(t))return 'written';return Array.isArray(q?.choices)&&Number.isInteger(q?.correct)?'multiple_choice':null},
 mix(items){const groups={multiple_choice:[],written:[],true_false:[]};for(const item of items){const q=item?.q&&typeof item.q==='object'?item.q:item;const k=this.kind(q);if(k)groups[k].push(item)}const shuffle=a=>{for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a};Object.values(groups).forEach(shuffle);const out=[],pattern=['multiple_choice','multiple_choice','written','multiple_choice','true_false','multiple_choice','multiple_choice','written','multiple_choice','multiple_choice'];while(Object.values(groups).some(a=>a.length)){for(const k of shuffle([...pattern]))if(groups[k].length)out.push(groups[k].shift())}return out}
};
/* Shared input and grading for the three supported question formats. */
window.MathWebQuestionMix.normalized=function(v){return String(v??'').normalize('NFKC').toLowerCase().trim().replace(/[−–]/g,'-').replace(/\s+/g,'').replace(/,/g,'.').replace(/\\cdot|×/g,'*')};
window.MathWebQuestionMix.grade=function(q,answer){
 const k=this.kind(q);if(k==='multiple_choice')return Number(answer)===q.correct;
 if(k==='true_false'){
  const normalize=v=>{const s=this.normalized(v);if(['true','đúng','dung','1','t'].includes(s))return true;if(['false','sai','0','f'].includes(s))return false;return null};
  const expected=normalize(q.answer??q.correct_answer??q.correct);return expected!==null&&normalize(answer)===expected;
 }
 const expected=q.answer??q.correct_answer??q.correct;
 if(expected===undefined||expected===null)return false;
 const a=this.normalized(answer),b=this.normalized(expected);
 if(a===b)return true;
 // Numeric equivalence only; never evaluate untrusted mathematical expressions.
 const numeric=v=>/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$/.test(v)?Number(v):null;
 const x=numeric(a),y=numeric(b);if(x!==null&&y!==null)return Math.abs(x-y)<=1e-9*Math.max(1,Math.abs(y));
 const alternatives=Array.isArray(q.accepted_answers)?q.accepted_answers:[];
 return alternatives.some(v=>this.normalized(v)===a);
};
window.MathWebQuestionMix.render=function(container,q,submit){
 container.replaceChildren();const k=this.kind(q);if(!k)return false;
 if(k==='multiple_choice'){
  q.choices.forEach((c,i)=>{const b=document.createElement('button');b.type='button';b.textContent=String.fromCharCode(65+i)+'. '+c;b.onclick=()=>submit(i,b);container.append(b)});return true;
 }
 if(k==='true_false'){
  for(const value of ['Đúng','Sai']){const b=document.createElement('button');b.type='button';b.textContent=value;b.onclick=()=>submit(value,b);container.append(b)}return true;
 }
 const input=document.createElement('input');input.type='text';input.placeholder='Nhập đáp án của bạn';input.setAttribute('aria-label','Câu trả lời');input.style.cssText='width:100%;min-height:42px;padding:10px;border:1px solid #9ca3af;border-radius:10px';
 const b=document.createElement('button');b.type='button';b.textContent='Kiểm tra đáp án';b.onclick=()=>{if(input.value.trim())submit(input.value.trim(),b)};
 input.onkeydown=e=>{if(e.key==='Enter'&&input.value.trim())submit(input.value.trim(),b)};container.append(input,b);return true;
};
window.MathWebQuestionMix.valid=function(q){const k=this.kind(q);if(!k)return false;if(k==='multiple_choice')return Array.isArray(q.choices)&&q.choices.length>=2&&Number.isInteger(q.correct)&&q.correct>=0&&q.correct<q.choices.length;return q.answer!==undefined||q.correct_answer!==undefined||q.correct!==undefined};
