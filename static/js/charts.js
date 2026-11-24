/* MalipoHub — dashboard charts (Chart.js loaded on demand) */
(function () {
  'use strict';

  // Placeholder: inject Chart.js and render a spend sparkline when a canvas exists.
  function loadChartJs(cb) {
    if (window.Chart) return cb();
    var s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/chart.js';
    s.onload = cb;
    document.head.appendChild(s);
  }

  document.addEventListener('DOMContentLoaded', function () {
    var canvas = document.getElementById('spendChart');
    if (!canvas) return;

    loadChartJs(function () {
      var ctx = canvas.getContext('2d');
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
          datasets: [{
            label: 'Settled spend',
            data: [0, 0, 0, 0],
            borderColor: '#2563EB',
            backgroundColor: 'rgba(37, 99, 235, 0.08)',
            fill: true,
            tension: 0.35,
            pointRadius: 3,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { display: false } },
            y: { beginAtZero: true, grid: { color: '#E2E8F0' } }
          }
        }
      });
    });
  });
})();