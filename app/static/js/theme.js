// Theme Management
const THEME_KEY = 'expenseiq_theme';

function getTheme() {
  return localStorage.getItem(THEME_KEY) || 'dark';
}

function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem(THEME_KEY, theme);
}

function toggleTheme() {
  const current = getTheme();
  const next = current === 'dark' ? 'light' : 'dark';
  setTheme(next);
  // Save to server if logged in
  fetch('/api/settings/theme', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ theme: next })
  }).catch(() => {});
}

// Apply theme on load
(function() {
  const saved = getTheme();
  document.documentElement.setAttribute('data-theme', saved);
})();
