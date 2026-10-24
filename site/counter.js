(async function () {
  const el = document.getElementById("visitor-count");
  const url = window.VISITOR_API_URL;
  if (!el || !url) return;
  try {
    const res = await fetch(url, { method: "POST" });
    if (!res.ok) throw new Error(res.status);
    const data = await res.json();
    el.textContent = data.count;
  } catch (err) {
    el.textContent = "unavailable";
    console.error("Visitor counter failed:", err);
  }
})();
