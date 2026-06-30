// ExpenseIQ Auth JS
let currentMobile = '';
let currentOTPPurpose = '';
let GOOGLE_CLIENT_ID = '';

function switchTab(tab, btn) {
  document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('emailTab').style.display = tab === 'email' ? 'block' : 'none';
  document.getElementById('otpTab').style.display = tab === 'otp' ? 'block' : 'none';
}

function togglePw(id, btn) {
  const input = document.getElementById(id);
  if (!input) return;
  input.type = input.type === 'password' ? 'text' : 'password';
}

// Add a graceful redirect that plays a leaving animation before navigation
function performRedirect(url, delay = 400) {
  try {
    const card = document.querySelector('.auth-card');
    if (card) card.classList.add('leaving');
  } catch (e) {}
  setTimeout(() => { window.location.href = url; }, delay);
}

async function loginEmail(e) {
  e.preventDefault();
  const btn = document.getElementById('loginBtn');
  const identifier = document.getElementById('loginIdentifier').value.trim();
  const password = document.getElementById('loginPassword').value;
  if (!identifier || !password) return showToast('Email or mobile and password are required', 'error');
  btn.textContent = 'Logging in...';
  btn.disabled = true;
  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ identifier, password, remember: document.getElementById('rememberMe') ? document.getElementById('rememberMe').checked : false })
    });
    const data = await res.json();
      if (data.success) {
        showToast('Login successful! Redirecting...', 'success');
        tryStoreCredentials(identifier, password);
        // signal dashboard to show logged-in banner
        try { localStorage.setItem('just_logged_in', '1'); } catch (e) {}
        performRedirect(data.redirect || '/dashboard', 900);
    } else {
      showToast(data.message || 'Login failed', 'error');
      btn.textContent = 'Log In';
      btn.disabled = false;
    }
  } catch (err) {
    showToast('Network error. Please try again.', 'error');
    btn.textContent = 'Log In';
    btn.disabled = false;
  }
}

async function registerUser(e) {
  e.preventDefault();
  const name = document.getElementById('signupName').value.trim();
  const email = document.getElementById('signupEmail').value.trim();
  const password = document.getElementById('signupPassword').value;
  const confirm = document.getElementById('signupConfirmPassword').value;
  const agree = document.getElementById('agreeTerms').checked;
  const username = document.getElementById('signupUsername').value.trim();
  const mobile = document.getElementById('signupMobile').value.trim().replace(/\D/g, '');
  if (!name || !username || !email || !mobile || !password || !confirm) return showToast('All fields are required', 'error');
  if (password !== confirm) return showToast('Passwords do not match', 'error');
  if (!agree) return showToast('Please agree to Terms of Service', 'error');
  if (password.length < 6) return showToast('Password must be at least 6 characters', 'error');
  if (mobile.length !== 10) return showToast('Enter a valid 10-digit mobile number', 'error');
  try {
    const res = await fetch('/api/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ full_name: name, username, email, mobile, password, confirm_password: confirm, remember: false })
    });
    const data = await res.json();
    if (data.success) {
        showToast('Account created! Please sign in to continue.', 'success');
        // attempt to store credentials in browser password manager (optional)
        tryStoreCredentials(email, password);
        // Redirect to login page so user can sign in
        performRedirect(data.redirect || '/login', 900);
    } else {
      showToast(data.message || 'Signup failed', 'error');
    }
  } catch (err) {
    showToast('Network error. Please try again.', 'error');
  }
}

async function sendOTP(purpose) {
  currentOTPPurpose = purpose;
  const mobileInput = purpose === 'login'
    ? document.getElementById('loginMobile')
    : document.getElementById('signupMobile');
  if (!mobileInput) return;
  const mobile = mobileInput.value.trim().replace(/\D/g, '');
  if (mobile.length !== 10) return showToast('Enter a valid 10-digit mobile number', 'error');
  currentMobile = mobile;
  try {
    const res = await fetch('/api/auth/send-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mobile, purpose })
    });
    const data = await res.json();
    if (data.success) {
      showToast(`OTP sent to ${mobile}`, 'success');
      if (data.dev_otp) {
        showToast(`[Dev Mode] OTP: ${data.dev_otp}`, 'info', 10000);
        autofillOTP(data.dev_otp, purpose);
      }
      if (purpose === 'login') {
        document.getElementById('otpStep1').style.display = 'none';
        document.getElementById('otpStep2').style.display = 'block';
        document.getElementById('otpMobileDisplay').textContent = mobile;
      } else {
        document.getElementById('mobileFieldSU').style.display = 'none';
        document.querySelector('#mobileSignupForm button[onclick="sendOTP(\'signup\')"]').style.display = 'none';
        document.getElementById('signupOTPStep').style.display = 'block';
        document.getElementById('signupMobileDisplay').textContent = mobile;
      }
      startResendTimer();
    } else {
      showToast(data.message || 'Failed to send OTP', 'error');
    }
  } catch (err) {
    showToast('Network error', 'error');
  }
}

function autofillOTP(otp, purpose) {
  setTimeout(() => {
    const boxes = document.querySelectorAll('.otp-box');
    otp.split('').forEach((d, i) => { if (boxes[i]) boxes[i].value = d; });
  }, 500);
}

function otpNext(input, idx) {
  const boxes = document.querySelectorAll('.otp-box');
  const val = input.value.replace(/\D/g, '');
  input.value = val;
  if (val && idx < boxes.length - 1) boxes[idx + 1].focus();
  if (!val && idx > 0) boxes[idx - 1].focus();
}

async function verifyOTP(purpose) {
  const boxes = document.querySelectorAll('.otp-box');
  const otp = Array.from(boxes).map(b => b.value).join('');
  if (otp.length < 6) return showToast('Enter complete 6-digit OTP', 'error');
  const body = { mobile: currentMobile, otp, purpose };
  if (purpose === 'signup') {
    const nameInput = document.getElementById('signupFullName');
    if (nameInput && nameInput.value.trim()) body.full_name = nameInput.value.trim();
  }
  try {
    const res = await fetch('/api/auth/verify-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    const data = await res.json();
    if (data.success) {
      showToast('Verified! Redirecting...', 'success');
      try { localStorage.setItem('just_logged_in', '1'); } catch (e) {}
      performRedirect(data.redirect || '/dashboard', 900);
    } else {
      showToast(data.message || 'Verification failed', 'error');
    }
  } catch (err) {
    showToast('Network error', 'error');
  }
}

async function resendOTP(purpose) {
  await sendOTP(purpose);
}

let resendTimer;
function startResendTimer() {
  const btn = document.getElementById('resendBtn');
  if (!btn) return;
  let sec = 30;
  btn.disabled = true;
  btn.textContent = `Resend in ${sec}s`;
  clearInterval(resendTimer);
  resendTimer = setInterval(() => {
    sec--;
    if (sec <= 0) {
      clearInterval(resendTimer);
      btn.disabled = false;
      btn.textContent = 'Resend OTP';
    } else {
      btn.textContent = `Resend in ${sec}s`;
    }
  }, 1000);
}

function googleLogin() {
  // If no client id, disable button and show a friendly tooltip
  if (!GOOGLE_CLIENT_ID) {
    const btn = document.getElementById('googleLoginBtn');
    if (btn) {
      btn.disabled = true;
      btn.title = 'Google Sign-In is currently unavailable.';
    }
    showToast('Google Sign-In is currently unavailable.', 'info');
    return;
  }
  // Open Google OAuth popup
  const redirect = window.location.origin + '/google_callback';
  const url = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${encodeURIComponent(GOOGLE_CLIENT_ID)}&response_type=id_token&scope=openid%20email%20profile&redirect_uri=${encodeURIComponent(redirect)}&nonce=${Date.now()}&prompt=select_account`;
  const popup = window.open(url, 'google_oauth', 'width=600,height=700');
  // listen for message from popup
  function onMessage(e) {
    if (e.origin !== window.location.origin) return;
    const data = e.data || {};
    if (data.success) {
      showToast('Google sign-in successful. Redirecting...', 'success');
      try { localStorage.setItem('just_logged_in', '1'); } catch (e) {}
      setTimeout(()=> window.location.href = data.payload && data.payload.redirect ? data.payload.redirect : '/dashboard', 700);
    } else {
      showToast(data.message || 'Google sign-in failed', 'error');
    }
    window.removeEventListener('message', onMessage);
  }
  window.addEventListener('message', onMessage);
}

// Fetch auth config on load
fetch('/api/auth/config').then(r=>r.json()).then(cfg=>{
  GOOGLE_CLIENT_ID = cfg.google_client_id || '';
  const btns = document.querySelectorAll('button[onclick^="googleLogin"]');
  btns.forEach(btn=>{
    if (!GOOGLE_CLIENT_ID) { btn.disabled = true; btn.title = 'Google Sign-In is currently unavailable.'; }
    else { btn.disabled = false; btn.title = ''; }
  });
}).catch(()=>{});

function showForgotPassword() {
  const modal = new bootstrap.Modal(document.getElementById('forgotModal'));
  modal.show();
}

async function submitForgotPassword() {
  const email = document.getElementById('forgotEmail').value.trim();
  if (!email) return showToast('Email is required', 'error');
  try {
    const res = await fetch('/api/auth/forgot-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    const data = await res.json();
    showToast(data.message, data.success ? 'success' : 'error');
    if (data.success) {
      document.getElementById('forgotStep1').style.display = 'none';
      document.getElementById('forgotStep2').style.display = 'block';
      if (data.dev_token) showToast(`[Dev] Reset token: ${data.dev_token}`, 'info', 15000);
    }
  } catch (err) {
    showToast('Network error', 'error');
  }
}

async function submitResetPassword() {
  const email = document.getElementById('forgotEmail').value.trim();
  const token = document.getElementById('resetToken').value.trim();
  const newPw = document.getElementById('newPassword').value;
  const confirmPw = document.getElementById('confirmNewPassword').value;
  if (!token || !newPw) return showToast('Token and new password required', 'error');
  if (newPw !== confirmPw) return showToast('Passwords do not match', 'error');
  try {
    const res = await fetch('/api/auth/reset-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, token, new_password: newPw })
    });
    const data = await res.json();
    showToast(data.message, data.success ? 'success' : 'error');
    if (data.success) performRedirect('/login', 900);
  } catch (err) {
    showToast('Network error', 'error');
  }
}

async function tryStoreCredentials(email, password) {
  // Try Credential Management API first
  try {
    if (window.PasswordCredential && navigator.credentials && navigator.credentials.store) {
      const cred = new PasswordCredential({ id: email, password: password });
      await navigator.credentials.store(cred);
      return;
    }
    if (navigator.credentials && navigator.credentials.create) {
      try {
        const c = await navigator.credentials.create({ password: { id: email, password: password } });
        if (c) await navigator.credentials.store(c);
        return;
      } catch(e){}
    }
  } catch (e) {}
  // Fallback: post to hidden iframe endpoint to trigger browser save prompt
  try {
    let iframe = document.getElementById('__savecred_iframe');
    if (!iframe) {
      iframe = document.createElement('iframe'); iframe.name = '__savecred_iframe'; iframe.id = '__savecred_iframe'; iframe.style.display = 'none'; document.body.appendChild(iframe);
    }
    const form = document.createElement('form');
    form.method = 'POST'; form.action = '/api/auth/silent-save-credential'; form.target = '__savecred_iframe';
    const i1 = document.createElement('input'); i1.type = 'hidden'; i1.name = 'email'; i1.value = email; form.appendChild(i1);
    const i2 = document.createElement('input'); i2.type = 'hidden'; i2.name = 'password'; i2.value = password; form.appendChild(i2);
    document.body.appendChild(form);
    form.submit();
    setTimeout(()=>{ try{ document.body.removeChild(form);}catch(e){} }, 2000);
  } catch(e){}
}

// Password strength meter
function passwordScore(pw) {
  let score = 0;
  if (!pw) return score;
  if (pw.length >= 8) score += 2;
  else if (pw.length >= 6) score += 1;
  if (/[A-Z]/.test(pw)) score += 1;
  if (/[0-9]/.test(pw)) score += 1;
  if (/[^A-Za-z0-9]/.test(pw)) score += 1;
  return score;
}

function updatePasswordStrength() {
  const el = document.getElementById('signupPassword');
  const display = document.getElementById('passwordStrength');
  if (!el || !display) return;
  const s = passwordScore(el.value);
  let text = 'Very weak';
  let color = 'var(--text-secondary)';
  if (s >= 5) { text = 'Very strong'; color = '#16a34a'; }
  else if (s >= 4) { text = 'Strong'; color = '#16a34a'; }
  else if (s >= 3) { text = 'Medium'; color = '#f59e0b'; }
  else if (s >= 2) { text = 'Weak'; color = '#f97316'; }
  display.textContent = `Password strength: ${text}`;
  display.style.color = color;
}

function initPasswordStrengthMeter() {
  const pw = document.getElementById('signupPassword');
  if (!pw) return;
  pw.addEventListener('input', updatePasswordStrength);
  updatePasswordStrength();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initPasswordStrengthMeter);
} else {
  initPasswordStrengthMeter();
}
