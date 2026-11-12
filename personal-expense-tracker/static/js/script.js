// Mobile sidebar toggle
document.getElementById("menuBtn").addEventListener("click", () => {
  document.getElementById("sidebar").classList.toggle("open");
});

// Confirm before deleting
document.querySelectorAll(".confirm-delete").forEach((f) => {
  f.addEventListener("submit", (e) => {
    if (!confirm("Delete this expense?")) e.preventDefault();
  });
});

// Charts (only on the dashboard)
const pie = document.getElementById("pieChart");
if (pie) {
  fetch("/api/chart-data").then((r) => r.json()).then((d) => {
    const colors = ["#6d28d9", "#4f46e5", "#8b5cf6", "#3b82f6", "#a78bfa", "#60a5fa", "#c4b5fd"];
    new Chart(pie, {
      type: "doughnut",
      data: { labels: d.categories.labels, datasets: [{ data: d.categories.values, backgroundColor: colors }] },
      options: { maintainAspectRatio: false, plugins: { legend: { position: "bottom" } } },
    });
    new Chart(document.getElementById("barChart"), {
      type: "bar",
      data: { labels: d.months.labels, datasets: [{ label: "₹ spent", data: d.months.values,
              backgroundColor: "#7c3aed", borderRadius: 8 }] },
      options: { maintainAspectRatio: false, plugins: { legend: { display: false } },
                 scales: { y: { beginAtZero: true } } },
    });
  });
}
