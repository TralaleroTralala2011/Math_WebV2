/* Optional API capability gate. Never turn a 404 into made-up learning stats.
   One /health check per page; pending calls share the same promise. */
(function(){
 'use strict';
 if(window.MATHWEB_OPTIONAL_API)return;
 var pending=null;
 function base(){return (window.MATHWEB_API_URL||'http://127.0.0.1:8000').replace(/\/+$/,'');}
 function capabilities(){
  if(pending)return pending;
  pending=(async function(){
    try {
      var controller=new AbortController();
      var timeout=setTimeout(function(){controller.abort();},7000);
      try {
        var response=await fetch(base()+'/health',{signal:controller.signal,cache:'no-store',mode:'cors'});
        if(!response.ok)return {};
        var data=await response.json();
        return data&&typeof data.features==='object'&&data.features||{};
      } finally {clearTimeout(timeout);}
    } catch(_) {return {};}
  })();
  return pending;
 }
 async function get(path,feature,token){
  if(!(await capabilities())[feature])return null;
  try {
    var r=await fetch(base()+path,{headers:{Authorization:'Bearer '+token}});
    if(!r.ok)return null;
    return await r.json();
  }catch(_){return null;}
 }
 window.MATHWEB_OPTIONAL_API={features:capabilities,get:get};
})();
