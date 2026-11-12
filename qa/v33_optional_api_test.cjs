// Reproducible gate test: old backend does not receive 404-causing optional requests.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const code=fs.readFileSync(__dirname+'/../js/optional-api-v33.js','utf8');
async function run(features){
 const calls=[];
 const context={
  window:{MATHWEB_API_URL:'https://math-webv2.onrender.com'},
  AbortController,clearTimeout,setTimeout,
  fetch:async(url)=>{calls.push(url);if(url.endsWith('/health'))return {ok:true,json:async()=>({features})};return {ok:true,json:async()=>({recommendations:[]})}},
 };
 vm.runInNewContext(code,context);
 const api=context.window.MATHWEB_OPTIONAL_API;
 const res=await Promise.all([
  api.get('/api/roadmap-v2/tutor/10','tutor_recommendations','test-token'),
  api.get('/api/roadmap-v2/status/10','roadmap_v2','test-token'),
  api.get('/api/games/activity-heatmap','activity_heatmap','test-token')
 ]);
 return {calls,res};
}
(async()=>{
 const old=await run({});assert.equal(old.calls.length,1);assert(old.calls[0].endsWith('/health'));
 assert(old.res.every(x=>x===null));
 const updated=await run({roadmap_v2:true,tutor_recommendations:true,activity_heatmap:true});
 assert.equal(updated.calls.length,4);assert(updated.res.every(x=>x!==null));
 console.log('PASS: old backend receives only 1 /health; updated backend receives 3 feature requests and 1 /health');
})().catch(e=>{console.error(e);process.exit(1)});
