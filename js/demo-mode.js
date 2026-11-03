(function(){
  const button=document.getElementById("tryMathWebBtn");
  if(!button)return;
  button.addEventListener("click",function(){
    // Isolate the real account session so trial actions cannot be attributed to it.
    if(localStorage.getItem("mathweb_trial_mode")!=="1"){
      for(const key of ["mathweb_token","mathweb_user","mathweb_profile"]){const value=localStorage.getItem(key);if(value!==null)localStorage.setItem("mathweb_pretrial_"+key,value);else localStorage.removeItem("mathweb_pretrial_"+key);localStorage.removeItem(key);}
    }
    localStorage.setItem("mathweb_trial_mode","1");
    localStorage.setItem("mathweb_trial_started_at",new Date().toISOString());
    if(!localStorage.getItem("mathweb_trial_profile")){
      localStorage.setItem("mathweb_trial_profile",JSON.stringify({username:"Khách trải nghiệm",role:"trial",trial:true}));
    }
    window.location.href="trial-practise.html?trial=1";
  });
})();
