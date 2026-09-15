// 主题切换（浅/深），持久化到 localStorage
window.__toggleTheme = function () {
  var cur = document.documentElement.hasAttribute("data-theme") ? "dark" : "light";
  var next = cur === "dark" ? "light" : "dark";
  applyTheme(next);
};
function applyTheme(mode) {
  if (mode === "dark") document.documentElement.setAttribute("data-theme", "dark");
  else document.documentElement.removeAttribute("data-theme");
  try { localStorage.setItem("theme", mode); } catch (e) {}
}
(function () {
  var saved = null;
  try { saved = localStorage.getItem("theme"); } catch (e) {}
  if (saved) applyTheme(saved);
})();
