import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { googleCompleteProfile } from '../services/api';
import logo from '../assets/logo minor.jpg';

const CompleteProfile = () => {
  const navigate       = useNavigate();
  const [searchParams] = useSearchParams();

  // Google data passed via URL params from Login/Register page
  const googleId = searchParams.get('google_id') || '';
  const email    = searchParams.get('email')     || '';
  const name     = decodeURIComponent(searchParams.get('name') || '');

  const [form, setForm]     = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError]   = useState('');
  const [showPass, setShowPass] = useState(false);

  useEffect(() => {
    // If someone lands here without google data, redirect them to register
    if (!googleId || !email) navigate('/register');
  }, [googleId, email]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await googleCompleteProfile({
        google_id: googleId,
        email,
        name,
        username: form.username,
        password: form.password,
      });
      localStorage.setItem('token', res.data.access_token);
      navigate('/onboarding');
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');
        .cp-root*{box-sizing:border-box}
        .cp-root{min-height:100vh;display:flex;align-items:center;justify-content:center;font-family:'Outfit',sans-serif;background:linear-gradient(135deg,#f0fdfb 0%,#e0f7fa 40%,#f0fdfa 70%,#ecfdf5 100%);padding:24px;position:relative;overflow:hidden}
        .cp-blobs{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
        .cp-blob{position:absolute;border-radius:50%;animation:cpDrift 14s ease-in-out infinite alternate}
        .cp-b1{width:520px;height:520px;background:radial-gradient(circle,rgba(6,182,212,.18),rgba(20,184,166,.06));top:-120px;left:-80px}
        .cp-b2{width:400px;height:400px;background:radial-gradient(circle,rgba(20,184,166,.16),rgba(6,182,212,.05));bottom:-80px;right:-60px;animation-delay:-5s}
        @keyframes cpDrift{0%{transform:translate(0,0) scale(1)}50%{transform:translate(30px,-25px) scale(1.07)}100%{transform:translate(-15px,20px) scale(.96)}}
        .cp-dotgrid{position:fixed;inset:0;z-index:0;pointer-events:none;background-image:radial-gradient(circle,rgba(6,182,212,.15) 1px,transparent 1px);background-size:28px 28px;opacity:.6}
        .cp-card{position:relative;z-index:1;width:100%;max-width:460px;background:rgba(255,255,255,.75);backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);border:1.5px solid rgba(6,182,212,.15);border-radius:28px;padding:44px 40px;box-shadow:0 0 0 1px rgba(6,182,212,.06),0 24px 64px rgba(6,182,212,.13),0 4px 16px rgba(0,0,0,.05);opacity:0;transform:translateY(28px);animation:cpUp .75s cubic-bezier(.16,1,.3,1) forwards .15s}
        .cp-deco{width:100%;height:4px;border-radius:100px;background:linear-gradient(90deg,#06b6d4,#14b8a6,#06b6d4);background-size:200% 100%;animation:cpShimmer 3s linear infinite;margin-bottom:28px}
        @keyframes cpShimmer{0%{background-position:0% 0}100%{background-position:200% 0}}
        .cp-logorow{display:flex;align-items:center;gap:12px;justify-content:center;margin-bottom:20px}
        .cp-logoimg{width:44px;height:44px;border-radius:12px;object-fit:contain;background:white;padding:4px;box-shadow:0 6px 16px rgba(6,182,212,.25)}
        .cp-logotext{font-size:18px;font-weight:800;color:#0f172a;letter-spacing:-.02em}
        .cp-logotext span{background:linear-gradient(135deg,#06b6d4,#0d9488);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
        .cp-google-info{background:rgba(6,182,212,.06);border:1.5px solid rgba(6,182,212,.15);border-radius:16px;padding:16px 18px;margin-bottom:24px;display:flex;align-items:center;gap:12px}
        .cp-google-avatar{width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#06b6d4,#0d9488);display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:700;color:white;flex-shrink:0}
        .cp-google-name{font-size:14px;font-weight:700;color:#0f172a}
        .cp-google-email{font-size:12px;color:#64748b;margin-top:2px}
        .cp-head{text-align:center;margin-bottom:24px}
        .cp-ctag{display:inline-block;font-size:11px;font-weight:700;color:#0891b2;background:rgba(6,182,212,.09);border:1px solid rgba(6,182,212,.2);padding:4px 12px;border-radius:100px;text-transform:uppercase;letter-spacing:.07em;margin-bottom:10px}
        .cp-ctitle{font-size:22px;font-weight:800;color:#0f172a;letter-spacing:-.02em;line-height:1.3}
        .cp-csub{font-size:13px;color:#94a3b8;margin-top:4px}
        .cp-field{margin-bottom:16px}
        .cp-field label{display:block;font-size:12px;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:.07em;margin-bottom:8px}
        .cp-iw{position:relative}
        .cp-iico{position:absolute;left:14px;top:50%;transform:translateY(-50%);font-size:15px;opacity:.4;pointer-events:none}
        .cp-field input{width:100%;padding:12px 14px 12px 42px;border-radius:13px;border:1.5px solid #e2e8f0;background:#f8fafc;color:#0f172a;font-family:'Outfit',sans-serif;font-size:14.5px;outline:none;transition:all .22s ease}
        .cp-field input:focus{border-color:#06b6d4;background:#f0fdfe;box-shadow:0 0 0 4px rgba(6,182,212,.1)}
        .cp-field input::placeholder{color:#cbd5e1}
        .cp-field input:disabled{background:#f1f5f9;color:#94a3b8;cursor:not-allowed}
        .cp-eye{position:absolute;right:12px;top:50%;transform:translateY(-50%);background:none;border:none;cursor:pointer;font-size:15px;opacity:.4;padding:4px;border-radius:6px;transition:opacity .2s}
        .cp-eye:hover{opacity:.8}
        .cp-err{background:#fef2f2;border:1.5px solid #fecaca;border-radius:12px;padding:11px 14px;font-size:13px;color:#dc2626;display:flex;align-items:center;gap:8px;margin-bottom:14px}
        .cp-submit{width:100%;padding:14px;border-radius:13px;border:none;cursor:pointer;font-family:'Outfit',sans-serif;font-size:15px;font-weight:700;color:#fff;background:linear-gradient(135deg,#06b6d4 0%,#0d9488 100%);box-shadow:0 8px 24px rgba(6,182,212,.38);transition:all .22s;margin-top:4px}
        .cp-submit:hover:not(:disabled){transform:translateY(-2px);box-shadow:0 14px 36px rgba(6,182,212,.48)}
        .cp-submit:disabled{opacity:.6;cursor:not-allowed}
        .cp-spin{display:inline-block;width:15px;height:15px;border:2px solid rgba(255,255,255,.35);border-top-color:#fff;border-radius:50%;animation:cpSpin .7s linear infinite;vertical-align:middle;margin-right:7px}
        @keyframes cpSpin{to{transform:rotate(360deg)}}
        @keyframes cpUp{to{opacity:1;transform:translateY(0)}}
      `}</style>

      <div className="cp-root">
        <div className="cp-blobs"><div className="cp-blob cp-b1"/><div className="cp-blob cp-b2"/></div>
        <div className="cp-dotgrid"/>

        <div className="cp-card">
          <div className="cp-deco"/>

          <div className="cp-logorow">
            <img src={logo} alt="AIMHHC" className="cp-logoimg"/>
            <span className="cp-logotext">AI<span>MH</span>HC</span>
          </div>

          {/* Google account info — pre-filled, read-only */}
          <div className="cp-google-info">
            <div className="cp-google-avatar">
              {name ? name[0].toUpperCase() : 'G'}
            </div>
            <div>
              <div className="cp-google-name">{name || 'Google User'}</div>
              <div className="cp-google-email">{email}</div>
            </div>
          </div>

          <div className="cp-head">
            <div className="cp-ctag">One Last Step</div>
            <h2 className="cp-ctitle">Complete your profile</h2>
            <p className="cp-csub">Choose a username and password to finish setup</p>
          </div>

          {error && <div className="cp-err">⚠️ <span>{error}</span></div>}

          <form onSubmit={handleSubmit}>
            {/* Email — pre-filled from Google, read-only */}
            <div className="cp-field">
              <label>Email (from Google)</label>
              <div className="cp-iw">
                <span className="cp-iico">📧</span>
                <input type="email" value={email} disabled/>
              </div>
            </div>

            {/* Username — user picks this */}
            <div className="cp-field">
              <label>Choose a Username</label>
              <div className="cp-iw">
                <span className="cp-iico">👤</span>
                <input
                  type="text"
                  placeholder="e.g. john_doe123"
                  value={form.username}
                  onChange={e => setForm({...form, username: e.target.value})}
                  required minLength={3} maxLength={30}
                  autoComplete="username"
                />
              </div>
            </div>

            {/* Password — user sets this (for manual login fallback) */}
            <div className="cp-field">
              <label>Set a Password</label>
              <div className="cp-iw">
                <span className="cp-iico">🔒</span>
                <input
                  type={showPass ? 'text' : 'password'}
                  placeholder="At least 6 characters"
                  value={form.password}
                  onChange={e => setForm({...form, password: e.target.value})}
                  required minLength={6}
                  autoComplete="new-password"
                />
                <button type="button" className="cp-eye" onClick={() => setShowPass(!showPass)}>
                  {showPass ? '🙈' : '👁️'}
                </button>
              </div>
            </div>

            <button type="submit" className="cp-submit" disabled={loading}>
              {loading ? <><span className="cp-spin"/>Creating your account...</> : 'Complete Setup →'}
            </button>
          </form>
        </div>
      </div>
    </>
  );
};

export default CompleteProfile;