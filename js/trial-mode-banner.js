(function(){
  const page=(location.pathname.split("/").pop()||"").toLowerCase();
  if(page!=="trial-practise.html" || new URLSearchParams(location.search).get("trial")!=="1")return;
  const bar=document.createElement("div");bar.id="mathwebTrialModeBanner";
  bar.style.cssText="position:sticky;top:0;z-index:99999;display:flex;align-items:center;justify-content:center;gap:12px;flex-wrap:wrap;padding:10px 14px;background:linear-gradient(90deg,#dcfce7,#dbeafe);border-bottom:1px solid #bfdbfe;color:#164e63;font:600 13px/1.4 Segoe UI,Arial,sans-serif";
  bar.innerHTML='<span>🧪 CHẾ ĐỘ DÙNG THỬ · Không cần đăng nhập · Chỉ có luyện tập · Tiến trình không ghi vào hồ sơ thật.</span><button type="button" id="exitMathWebTrial" style="border:0;border-radius:999px;background:#0f766e;color:white;padding:7px 12px;font-weight:700;cursor:pointer">Thoát dùng thử</button>';
  document.body.prepend(bar);document.getElementById("exitMathWebTrial").addEventListener("click",function(){for(const key of ["mathweb_token","mathweb_user","mathweb_profile"]){const saved=localStorage.getItem("mathweb_pretrial_"+key);if(saved!==null)localStorage.setItem(key,saved);else localStorage.removeItem(key);localStorage.removeItem("mathweb_pretrial_"+key);}localStorage.removeItem("mathweb_trial_mode");location.href="index.html";});
})();
