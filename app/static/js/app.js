// App-specific JS (loaded on dashboard pages)
document.addEventListener('DOMContentLoaded', function() {
  // Update unread count periodically
  if (document.querySelector('.notif-dot')) {
    setInterval(updateNotifCount, 60000);
  }
  
  // Close profile dropdown when clicking outside
  document.addEventListener('click', function(event) {
    const dropdown = document.getElementById('profileDropdown');
    const wrapper = document.querySelector('.profile-dropdown-wrapper');
    if (dropdown && wrapper && !wrapper.contains(event.target)) {
      dropdown.classList.remove('show');
    }
  });
  
  // Close profile dropdown on Escape key
  document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
      const dropdown = document.getElementById('profileDropdown');
      if (dropdown) {
        dropdown.classList.remove('show');
      }
    }
  });
});

// Profile dropdown toggle
function toggleProfileDropdown(event) {
  event.stopPropagation();
  const dropdown = document.getElementById('profileDropdown');
  if (dropdown) {
    dropdown.classList.toggle('show');
  }
}

async function updateNotifCount() {
  try {
    const res = await fetch('/api/notifications/count');
    const data = await res.json();
    const dot = document.querySelector('.notif-dot');
    const badge = document.querySelector('.nav-badge');
    if (data.success) {
      const count = data.count;
      if (dot) {
        dot.textContent = count;
        dot.style.display = count > 0 ? 'flex' : 'none';
      }
      if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'block' : 'none';
      }
    }
  } catch (e) {}
}

// Category color mapping
const CATEGORY_COLORS = {
  'Food & Dining': '#f59e0b',
  'Transportation': '#3b82f6',
  'Shopping': '#8b5cf6',
  'Bills & Utilities': '#ef4444',
  'Entertainment': '#ec4899',
  'Healthcare': '#10b981',
  'Education': '#06b6d4',
  'Travel': '#f97316',
  'Groceries': '#22c55e',
  'Rent & Housing': '#6366f1',
  'Personal Care': '#a78bfa',
  'Investments': '#14b8a6',
  'Others': '#6b7280',
};

function getCategoryColor(category) {
  return CATEGORY_COLORS[category] || '#6b7280';
}

function getCategoryColors(categories) {
  return categories.map(getCategoryColor);
}
