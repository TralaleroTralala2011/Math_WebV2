/* MATA learner profile + evidence dashboard. XP remains a separate game metric. */
(() => {
  "use strict";
  const base = window.MATHWEB_API_BASE || "http://127.0.0.1:8000";
  const token = () => localStorage.getItem("mathweb_token") || "";
  const el = (id) => document.getElementById(id);
  const escapeHtml = (v) => String(v ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  async function get(path) {
    const response = await fetch(base + path, {headers:{Accept:"application/json",Authorization:"Bearer " + token()}});
    if (!response.ok) throw new Error(response.status === 401 ? "Vui lòng đăng nhập để xem hồ sơ học tập." : "Không tải được dữ liệu học tập.");
    return response.json();
  }
  async function load() {
    const status = el("mataStatus");
    if (!status) return;
    if (!token()) { status.textContent = "Đăng nhập để MATA bắt đầu xây dựng hồ sơ kỹ năng và thống kê quá trình luyện tập."; return; }
    status.textContent = "Đang đồng bộ dữ liệu học tập…";
    try {
      const [profile, recommendations, dashboard] = await Promise.all([
        get("/api/ai/mata/profile"), get("/api/ai/mata/recommendations?grade=10"), get("/api/ai/analytics/dashboard")
      ]);
      const summary = dashboard.summary || {};
      el("mataStats").innerHTML = `
        <article class="mata-stat"><small>Số câu đã làm</small><strong>${summary.attempts || 0}</strong></article>
        <article class="mata-stat"><small>Số câu đúng</small><strong>${summary.correct || 0}</strong></article>
        <article class="mata-stat"><small>Ngày có hoạt động</small><strong>${summary.active_days || 0}</strong></article>`;
      const skills = profile.skills || [];
      el("mataSkills").innerHTML = skills.length ? skills.map(s => `<div class="mata-line"><span>${escapeHtml(s.topic)}</span><strong>${Number(s.mastery || 0).toFixed(1)}%</strong><small>${s.correct}/${s.attempts} câu đúng</small></div>`).join("") : "Chưa đủ dữ liệu. Hãy hoàn thành một số câu luyện tập để tạo hồ sơ kỹ năng.";
      const teacher = el("mataTeacherFeedback");
      if (teacher) teacher.textContent = recommendations.teacher_feedback || "Hãy tiếp tục luyện tập để MATA có thêm dữ liệu nhận xét.";
      const recs = recommendations.recommendations || [];
      el("mataRecommendations").innerHTML = recs.length ? recs.slice(0,5).map(r => `<div class="mata-line"><span><b>${escapeHtml(r.name)}</b><small>${escapeHtml(r.reason)}<br>${escapeHtml(r.advice || "")}</small></span><strong>${escapeHtml(r.difficulty)}</strong></div>`).join("") : "Chưa có đề xuất.";
      const days = dashboard.by_day || [];
      el("mataHistory").innerHTML = days.length ? days.slice(-10).reverse().map(d => `<div class="mata-line"><span>${escapeHtml(d.day)}</span><strong>${d.correct}/${d.attempts} đúng</strong></div>`).join("") : "Chưa có lịch sử trả lời.";
      status.textContent = "Dữ liệu được tổng hợp từ lịch sử trả lời thực tế. Điểm XP trò chơi không được dùng làm điểm năng lực.";
    } catch (error) { status.textContent = error.message; }
  }
  document.addEventListener("DOMContentLoaded", load, {once:true});
})();
