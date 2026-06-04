
  // Redirect if already logged in
  if (localStorage.getItem('access_token')) window.location.href = '/dashboard.html';

  function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach((b,i) => b.classList.toggle('active', (i===0&&tab==='login')||(i===1&&tab==='register')));
    document.getElementById('panel-login').classList.toggle('active', tab==='login');
    document.getElementById('panel-register').classList.toggle('active', tab==='register');
  }

  function setLoading(btnId, loading) {
    const btn = document.getElementById(btnId);
    btn.disabled = loading;
    btn.innerHTML = loading ? '<span class="btn-loader"></span>Loading…' : btn.dataset.label;
  }

  document.querySelectorAll('.btn-primary').forEach(b => b.dataset.label = b.textContent);

  function showAlert(id, msg, type='error') {
    const el = document.getElementById(id);
    el.textContent = msg;
    el.className = `alert ${type} show`;
  }
  function hideAlert(id) {
    document.getElementById(id).className = 'alert';
  }

  async function doLogin() {
    hideAlert('login-error');
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;
    if (!email || !password) return showAlert('login-error', 'Please fill in all fields.');
    setLoading('login-btn', true);
    try {
      const res = await fetch('/api/login/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email, password})
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.non_field_errors?.[0] || 'Invalid credentials');
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      window.location.href = '/dashboard.html';
    } catch(e) {
      showAlert('login-error', e.message);
    } finally {
      setLoading('login-btn', false);
    }
  }

  async function doRegister() {
    hideAlert('register-error');
    hideAlert('register-success');
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;
    const first_name = document.getElementById('reg-first').value.trim();
    const last_name = document.getElementById('reg-last').value.trim();
    if (!email || !password) return showAlert('register-error', 'Email and password are required.');
    setLoading('register-btn', true);
    try {
      const res = await fetch('/api/users/register/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email, password, first_name, last_name})
      });
      const data = await res.json();
      if (!res.ok) {
        const msg = data.email?.[0] || data.password?.[0] || data.detail || 'Registration failed.';
        throw new Error(msg);
      }
      showAlert('register-success', 'Account created! Signing you in…', 'success');
      // Auto-login
      const lr = await fetch('/api/users/login/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email, password})
      });
      const ld = await lr.json();
      if (lr.ok) {
        localStorage.setItem('access_token', ld.access);
        localStorage.setItem('refresh_token', ld.refresh);
        setTimeout(() => window.location.href = '/dashboard.html', 800);
      }
    } catch(e) {
      showAlert('register-error', e.message);
    } finally {
      setLoading('register-btn', false);
    }
  }

  // Allow Enter key
  document.addEventListener('keydown', e => {
    if (e.key !== 'Enter') return;
    if (document.getElementById('panel-login').classList.contains('active')) doLogin();
    else doRegister();
  });
