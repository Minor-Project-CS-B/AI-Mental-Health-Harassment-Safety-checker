import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../services/api';
import logo from '../assets/logo minor.jpg';

const Login = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPass, setShowPass] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await login(form.username, form.password);
      localStorage.setItem('token', res.data.access_token);
      navigate('/onboarding');
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Invalid username or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Playfair+Display:ital,wght@0,800;1,700&display=swap');

        .lg-root * { box-sizing: border-box; }
        .lg-root {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          font-family: 'Outfit', sans-serif;
          background: linear-gradient(135deg, #f0fdfb 0%, #e0f7fa 40%, #f0fdfa 70%, #ecfdf5 100%);
          position: relative;
          overflow: hidden;
          padding: 24px;
        }

        .lg-blobs { position: fixed; inset: 0; z-index: 0; pointer-events: none; overflow: hidden; }
        .lg-blob { position: absolute; border-radius: 50%; animation: lgDrift 14s ease-in-out infinite alternate; }
        .lg-b1 { width: 520px; height: 520px; background: radial-gradient(circle, rgba(6,182,212,.18), rgba(20,184,166,.06)); top: -120px; left: -80px; }
        .lg-b2 { width: 400px; height: 400px; background: radial-gradient(circle, rgba(20,184,166,.16), rgba(6,182,212,.05)); bottom: -80px; right: -60px; animation-delay: -5s; }
        .lg-b3 { width: 280px; height: 280px; background: radial-gradient(circle, rgba(6,182,212,.1), transparent); top: 45%; left: 48%; animation-delay: -9s; }
        @keyframes lgDrift {
          0%   { transform: translate(0,0) scale(1); }
          50%  { transform: translate(30px,-25px) scale(1.07); }
          100% { transform: translate(-15px,20px) scale(.96); }
        }
        .lg-dotgrid {
          position: fixed; inset: 0; z-index: 0; pointer-events: none;
          background-image: radial-gradient(circle, rgba(6,182,212,.15) 1px, transparent 1px);
          background-size: 28px 28px; opacity: .6;
        }

        .lg-card {
          position: relative; z-index: 1;
          width: 100%; max-width: 440px;
          background: rgba(255,255,255,.75);
          backdrop-filter: blur(24px);
          -webkit-backdrop-filter: blur(24px);
          border: 1.5px solid rgba(6,182,212,.15);
          border-radius: 28px;
          padding: 44px 40px;
          box-shadow:
            0 0 0 1px rgba(6,182,212,.06),
            0 24px 64px rgba(6,182,212,.13),
            0 4px 16px rgba(0,0,0,.05);
          opacity: 0;
          transform: translateY(28px);
          animation: lgUp .75s cubic-bezier(.16,1,.3,1) forwards .15s;
        }

        .lg-deco {
          width: 100%; height: 4px; border-radius: 100px;
          background: linear-gradient(90deg, #06b6d4, #14b8a6, #06b6d4);
          background-size: 200% 100%;
          animation: lgShimmer 3s linear infinite;
          margin-bottom: 32px;
        }
        @keyframes lgShimmer { 0% { background-position: 0% 0; } 100% { background-position: 200% 0; } }

        /* Logo row */
        .lg-logorow {
          display: flex; align-items: center; gap: 12px;
          justify-content: center; margin-bottom: 24px;
          opacity: 0; transform: translateY(14px);
          animation: lgUp .6s ease forwards .3s;
        }
        .lg-logoimg {
          width: 48px; height: 48px;
          border-radius: 14px;
          object-fit: contain;
          background: white;
          padding: 4px;
          box-shadow: 0 8px 20px rgba(6,182,212,.25), inset 0 1px 0 rgba(255,255,255,.3);
        }
        .lg-logotext { font-size: 20px; font-weight: 800; color: #0f172a; letter-spacing: -.02em; }
        .lg-logotext span { background: linear-gradient(135deg,#06b6d4,#0d9488); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }

        .lg-head {
          text-align: center; margin-bottom: 32px;
          opacity: 0; transform: translateY(14px);
          animation: lgUp .6s ease forwards .42s;
        }
        .lg-ctag {
          display: inline-block; font-size: 11px; font-weight: 700; color: #0891b2;
          background: rgba(6,182,212,.09); border: 1px solid rgba(6,182,212,.2);
          padding: 4px 12px; border-radius: 100px;
          text-transform: uppercase; letter-spacing: .07em; margin-bottom: 12px;
        }
        .lg-ctitle { font-size: 26px; font-weight: 800; color: #0f172a; letter-spacing: -.02em; line-height: 1.2; }
        .lg-csub { font-size: 14px; color: #94a3b8; margin-top: 6px; }

        .lg-form {
          opacity: 0; transform: translateY(14px);
          animation: lgUp .6s ease forwards .54s;
        }
        .lg-field { margin-bottom: 18px; }
        .lg-field label {
          display: block; font-size: 12px; font-weight: 700; color: #475569;
          text-transform: uppercase; letter-spacing: .07em; margin-bottom: 9px;
        }
        .lg-iw { position: relative; }
        .lg-iico {
          position: absolute; left: 14px; top: 50%; transform: translateY(-50%);
          font-size: 15px; opacity: .4; pointer-events: none;
        }
        .lg-field input {
          width: 100%; padding: 13px 14px 13px 42px;
          border-radius: 13px; border: 1.5px solid #e2e8f0;
          background: #f8fafc; color: #0f172a;
          font-family: 'Outfit', sans-serif; font-size: 14.5px;
          outline: none; transition: all .22s ease;
        }
        .lg-field input::placeholder { color: #cbd5e1; }
        .lg-field input:focus {
          border-color: #06b6d4; background: #f0fdfe;
          box-shadow: 0 0 0 4px rgba(6,182,212,.1);
        }
        .lg-eye {
          position: absolute; right: 12px; top: 50%; transform: translateY(-50%);
          background: none; border: none; cursor: pointer;
          font-size: 15px; opacity: .4; transition: opacity .2s;
          padding: 4px; border-radius: 6px;
        }
        .lg-eye:hover { opacity: .8; background: rgba(6,182,212,.08); }

        .lg-err {
          background: #fef2f2; border: 1.5px solid #fecaca;
          border-radius: 12px; padding: 11px 14px;
          font-size: 13px; color: #dc2626;
          display: flex; align-items: center; gap: 8px;
          margin-bottom: 16px;
          animation: lgShake .4s ease;
          box-shadow: 0 4px 12px rgba(239,68,68,.08);
        }
        @keyframes lgShake { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-5px)} 75%{transform:translateX(5px)} }

        .lg-submit {
          width: 100%; padding: 14px; border-radius: 13px; border: none;
          cursor: pointer; font-family: 'Outfit', sans-serif;
          font-size: 15px; font-weight: 700; letter-spacing: .02em;
          color: #fff;
          background: linear-gradient(135deg, #06b6d4 0%, #0d9488 100%);
          box-shadow: 0 8px 24px rgba(6,182,212,.38), inset 0 1px 0 rgba(255,255,255,.15);
          transition: all .22s; margin-top: 6px;
          position: relative; overflow: hidden;
        }
        .lg-submit::before {
          content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255,255,255,.2), transparent);
          transition: left .5s ease;
        }
        .lg-submit:hover:not(:disabled)::before { left: 100%; }
        .lg-submit:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 14px 36px rgba(6,182,212,.48), inset 0 1px 0 rgba(255,255,255,.15);
        }
        .lg-submit:active:not(:disabled) { transform: translateY(0); }
        .lg-submit:disabled { opacity: .6; cursor: not-allowed; }

        .lg-spin {
          display: inline-block; width: 15px; height: 15px;
          border: 2px solid rgba(255,255,255,.35); border-top-color: #fff;
          border-radius: 50%; animation: lgSpin .7s linear infinite;
          vertical-align: middle; margin-right: 7px;
        }
        @keyframes lgSpin { to { transform: rotate(360deg); } }

        .lg-or { display: flex; align-items: center; gap: 12px; margin: 18px 0; }
        .lg-orl { flex: 1; height: 1px; background: linear-gradient(90deg, transparent, #e2e8f0, transparent); }
        .lg-ort { font-size: 12px; color: #94a3b8; font-weight: 600; white-space: nowrap; }

        .lg-regbtn {
          width: 100%; padding: 13px; border-radius: 13px;
          border: 1.5px solid #e2e8f0; background: white;
          cursor: pointer; font-family: 'Outfit', sans-serif;
          font-size: 14px; font-weight: 600; color: #374151;
          display: flex; align-items: center; justify-content: center; gap: 9px;
          transition: all .22s; text-decoration: none;
          box-shadow: 0 2px 8px rgba(0,0,0,.04);
        }
        .lg-regbtn:hover {
          border-color: #06b6d4; background: #f0fdfe;
          color: #0891b2; transform: translateY(-1px);
          box-shadow: 0 6px 20px rgba(6,182,212,.12);
        }

        .lg-trust {
          display: flex; align-items: center; justify-content: center;
          gap: 6px; margin-top: 22px; padding-top: 20px;
          border-top: 1px solid #f1f5f9; flex-wrap: wrap;
          opacity: 0; transform: translateY(10px);
          animation: lgUp .6s ease forwards .7s;
        }
        .lg-ti {
          display: flex; align-items: center; gap: 4px;
          font-size: 11px; color: #94a3b8; font-weight: 600;
          padding: 4px 10px; border-radius: 100px;
          background: rgba(6,182,212,.05); border: 1px solid rgba(6,182,212,.1);
        }

        @keyframes lgUp { to { opacity: 1; transform: translateY(0); } }
      `}</style>

      <div className="lg-root">
        <div className="lg-blobs">
          <div className="lg-blob lg-b1"/>
          <div className="lg-blob lg-b2"/>
          <div className="lg-blob lg-b3"/>
        </div>
        <div className="lg-dotgrid"/>

        <div className="lg-card">
          <div className="lg-deco"/>

          <div className="lg-logorow">
            <img src={logo} alt="AIMHHC Logo" className="lg-logoimg" />
            <span className="lg-logotext">AI<span>MH</span>HC</span>
          </div>

          <div className="lg-head">
            <div className="lg-ctag">Secure Login</div>
            <h2 className="lg-ctitle">Welcome back! 👋</h2>
            <p className="lg-csub">Your wellness journey continues here</p>
          </div>

          {error && (
            <div className="lg-err">⚠️ <span>{String(error)}</span></div>
          )}

          <form className="lg-form" onSubmit={handleLogin}>
            <div className="lg-field">
              <label>Username</label>
              <div className="lg-iw">
                <span className="lg-iico">👤</span>
                <input
                  type="text"
                  placeholder="Enter your username"
                  value={form.username}
                  onChange={e => setForm({...form, username: e.target.value})}
                  required autoComplete="username"
                />
              </div>
            </div>

            <div className="lg-field">
              <label>Password</label>
              <div className="lg-iw">
                <span className="lg-iico">🔒</span>
                <input
                  type={showPass ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={form.password}
                  onChange={e => setForm({...form, password: e.target.value})}
                  required autoComplete="current-password"
                />
                <button type="button" className="lg-eye" onClick={() => setShowPass(!showPass)}>
                  {showPass ? '🙈' : '👁️'}
                </button>
              </div>
            </div>

            <button type="submit" className="lg-submit" disabled={loading}>
              {loading ? <><span className="lg-spin"/>Signing in...</> : 'Sign In →'}
            </button>
          </form>

          <div className="lg-or">
            <div className="lg-orl"/>
            <span className="lg-ort">Don't have an account?</span>
            <div className="lg-orl"/>
          </div>

          <a href="/register" className="lg-regbtn">✨ Create a Free Account</a>

          <div className="lg-trust">
            <div className="lg-ti">🔒 SSL Secured</div>
            <div className="lg-ti">🛡️ Private</div>
            <div className="lg-ti">✨ No Ads</div>
            <div className="lg-ti">💚 Non-diagnostic</div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Login;