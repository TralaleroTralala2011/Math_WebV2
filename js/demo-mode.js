(function(){
  "use strict";
  const banner=document.getElementById("mathwebTrialBanner");
  const button=document.getElementById("tryMathWebBtn");
  if(!banner)return;
  function signedIn(){
    try{return Boolean(localStorage.getItem("mathweb_token")||localStorage.getItem("mathweb_admin_token"));}
    catch(_){return false;}
  }
  banner.hidden=signedIn();
  if(!button)return;
  button.addEventListener("click",function(){
    // Trial must never remove or replace an authenticated session.
    if(signedIn()){banner.hidden=true;return;}
    try{
      localStorage.setItem("mathweb_trial_mode","1");
      localStorage.setItem("mathweb_trial_started_at",new Date().toISOString());
      if(!localStorage.getItem("mathweb_trial_profile")){
        localStorage.setItem("mathweb_trial_profile",JSON.stringify({username:"Khách trải nghiệm",role:"trial",trial:true}));
      }
    }catch(_){}
    location.href="trial-practise.html?trial=1";
  });
})();
