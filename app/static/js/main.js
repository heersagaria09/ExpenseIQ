// ExpenseIQ Main JS

// CRITICAL: Prevent white flash during page navigation
(function() {
  // Add loading class to disable transitions during navigation
  document.documentElement.classList.add('loading');
  
  // Remove loading class after everything loads
  window.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
      document.documentElement.classList.remove('loading');
    }, 50);
  });
})();

function showToast(message, type = 'info', duration = 4000) {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const icons = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' };
  const toast = document.createElement('div');
  toast.className = `toast-custom toast-${type}`;
  toast.innerHTML = `<span class="toast-icon">${icons[type] || 'ℹ'}</span><span class="toast-message">${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = '0.3s';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  if (!sidebar) return;
  sidebar.classList.toggle('open');
  if (overlay) overlay.classList.toggle('open');
}

function formatCurrency(amount) {
  if (isNaN(amount)) return '₹0.00';
  return '₹' + parseFloat(amount).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (isNaN(d)) return dateStr;
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}

async function apiRequest(url, method = 'GET', body = null) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  const data = await res.json();
  return data;
}

function confirmDelete(message = 'Are you sure you want to delete this?') {
  return confirm(message);
}

// Chart defaults
if (typeof Chart !== 'undefined') {
  Chart.defaults.color = '#8b9ab8';
  Chart.defaults.borderColor = '#1e2d45';
  Chart.defaults.font.family = "'Inter', sans-serif";
  Chart.defaults.plugins.legend.labels.boxWidth = 12;
  Chart.defaults.plugins.legend.labels.padding = 16;
}

function createLineChart(ctx, labels, datasets, options = {}) {
  return new Chart(ctx, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'top' }, tooltip: { mode: 'index', intersect: false } },
      scales: {
        x: { grid: { color: '#1e2d45' } },
        y: {
          grid: { color: '#1e2d45' },
          ticks: { callback: v => '₹' + v.toLocaleString('en-IN') }
        }
      },
      ...options
    }
  });
}

function createDoughnutChart(ctx, labels, data, colors, options = {}) {
  return new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{ data, backgroundColor: colors, borderWidth: 0, spacing: 2 }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'right' },
        tooltip: { callbacks: { label: ctx => ` ₹${ctx.raw.toLocaleString('en-IN')}` } }
      },
      cutout: '65%',
      ...options
    }
  });
}

function createBarChart(ctx, labels, datasets, options = {}) {
  return new Chart(ctx, {
    type: 'bar',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'top' } },
      scales: {
        x: { grid: { display: false } },
        y: {
          grid: { color: '#1e2d45' },
          ticks: { callback: v => '₹' + v.toLocaleString('en-IN') }
        }
      },
      ...options
    }
  });
}

// Show a welcome toast if redirected here after login
document.addEventListener('DOMContentLoaded', () => {
  try {
    const flag = localStorage.getItem('just_logged_in');
    if (flag) {
      localStorage.removeItem('just_logged_in');
      showToast('You have logged in successfully', 'success', 4000);
    }
  } catch (e) {}
});
