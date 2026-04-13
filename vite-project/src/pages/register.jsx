import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { register } from '../services/api';
import logo from '../assets/logo minor.jpg';

const Register = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState({ fullName: '', username: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPass, setShowPass] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await register({
        name: form.fullName,
        username: form.username,
        email: form.email,
        password: form.password
      });
      navigate('/login');
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail[0].msg);
      } else {
        setError(detail || 'Registration failed.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

        .rg-root * { box-sizing: border-box; }
        .rg-root {
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

        .rg-blobs { position: fixed; inset: 0; z-index: 0; pointer-events: none; overflow: hidden; }
        .rg-blob { position: absolute; border-radius: 50%; animation: rgDrift 14s ease-in-out infinite alternate; }
        .rg-b1 { width: 520px; height: 520px; background: radial-gradient(circle, rgba(6,182,212,.18), rgba(20,184,166,.06)); top: -120px; left: -80px; }
        .rg-b2 { width: 400px; height: 400px; background: radial-gradient(circle, rgba(20,184,166,.16), rgba(6,182,212,.05)); bottom: -80px; right: -60px; animation-delay: -5s; }
        .rg-b3 { width: 280px; height: 280px; background: radial-gradient(circle, rgba(6,182,212,.1), transparent); top: 45%; left: 48%; animation-delay: -9s; }
        @keyframes rgDrift {
          0%   { transform: translate(0,0) scale(1); }
          50%  { transform: translate(30px,-25px) scale(1.07); }
          100% { transform: translate(-15px,20px) scale(.96); }
        }
        .rg-dotgrid {
          position: fixed; inset: 0; z-index: 0; pointer-events: none;
          background-image: radial-gradient(circle, rgba(6,182,212,.15) 1px, transparent 1px);
          background-size: 28px 28px; opacity: .6;
        }

        .rg-card {
          position: relative; z-index: 1;
          width: 100%; max-width: 460px;
          background: rgba(255,255,255,.75);
          backdrop-filter: blur(24px);
          -webkit-backdrop-filter: blur(24px);
          border: 1.5px solid rgba(6,182,212,.15);
          border-radius: 28px;
          padding: 40px 40px;
          box-shadow:
            0 0 0 1px rgba(6,182,212,.06),
            0 24px 64px rgba(6,182,212,.13),
            0 4px 16px rgba(0,0,0,.05);
          opacity: 0;
          transform: translateY(28px);
          animation: rgUp .75s cubic-bezier(.16,1,.3,1) forwards .15s;
        }

        .rg-deco {
          width: 100%; height: 4px; border-radius: 100px;
          background: linear-gradient(90deg, #06b6d4, #14b8a6, #06b6d4);
          background-size: 200% 100%;
          animation: rgShimmer 3s linear infinite;
          margin-bottom: 28px;
        }
        @keyframes rgShimmer { 0% { background-position: 0% 0; } 100% { background-position: 200% 0; } }

        .rg-logorow {
          display: flex; align-items: center; gap: 12px;
          justify-content: center; margin-bottom: 20px;
          opacity: 0; transform: translateY(14px);
          animation: rgUp .6s ease forwards .3s;
        }
        .rg-logoimg {
          width: 48px; height: 48px;
          border-radius: 14px;
          object-fit: contain;
          background: white;
          padding: 4px;
          box-shadow: 0 8px 20px rgba(6,182,212,.25), inset 0 1px 0 rgba(255,255,255,.3);
        }
        .rg-logotext { font-size: 20px; font-weight: 800; color: #0f172a; letter-spacing: -.02em; }
        .rg-logotext span { background: linear-gradient(135deg,#06b6d4,#0d9488); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }

        .rg-head {
          text-align: center; margin-bottom: 28px;
          opacity: 0; transform: translateY(14px);
          animation: rgUp .6s ease forwards .4s;
        }
        .rg-ctag {
          display: inline-block; font-size: 11px; font-weight: 700; color: #0891b2;
          background: rgba(6,182,212,.09); border: 1px solid rgba(6,182,212,.2);
          padding: 4px 12px; border-radius: 100px;
          text-transform: uppercase; letter-spacing: .07em; margin-bottom: 10px;
        }
        .rg-ctitle { font-size: 25px; font-weight: 800; color: #0f172a; letter-spacing: -.02em; line-height: 1.2; }
        .rg-csub { font-size: 13.5px; color: #94a3b8; margin-top: 5px; }

        .rg-form {
          opacity: 0; transform: translateY(14px);
          animation: rgUp .6s ease forwards .52s;
        }
        .rg-field { margin-bottom: 15px; }
        .rg-field label {
          display: block; font-size: 12px; font-weight: 700; color: #475569;
          text-transform: uppercase; letter-spacing: .07em; margin-bottom: 8px;
        }
        .rg-iw { position: relative; }
        .rg-iico {
          position: absolute; left: 14px; top: 50%; transform: translateY(-50%);
          font-size: 15px; opacity: .4; pointer-events: none;
        }
        .rg-field input {
          width: 100%; padding: 12px 14px 12px 42px;
          border-radius: 13px; border: 1.5px solid #e2e8f0;
          background: #f8fafc; color: #0f172a;
          font-family: 'Outfit', sans-serif; font-size: 14.5px;
          outline: none; transition: all .22s ease;
        }
        .rg-field input::placeholder { color: #cbd5e1; }
        .rg-field input:focus {
          border-color: #06b6d4; background: #f0fdfe;
          box-shadow: 0 0 0 4px rgba(6,182,212,.1);
        }
        .rg-eye {
          position: absolute; right: 12px; top: 50%; transform: translateY(-50%);
          background: none; border: none; cursor: pointer;
          font-size: 15px; opacity: .4; transition: opacity .2s;
          padding: 4px; border-radius: 6px;
        }
        .rg-eye:hover { opacity: .8; background: rgba(6,182,212,.08); }

        .rg-err {
          background: #fef2f2; border: 1.5px solid #fecaca;
          border-radius: 12px; padding: 11px 14px;
          font-size: 13px; color: #dc2626;
          display: flex; align-items: center; gap: 8px;
          margin-bottom: 14px;
          animation: rgShake .4s ease;
          box-shadow: 0 4px 12px rgba(239,68,68,.08);
        }
        @keyframes rgShake { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-5px)} 75%{transform:translateX(5px)} }

        .rg-submit {
          width: 100%; padding: 14px; border-radius: 13px; border: none;
          cursor: pointer; font-family: 'Outfit', sans-serif;
          font-size: 15px; font-weight: 700; letter-spacing: .02em;
          color: #fff;
          background: linear-gradient(135deg, #06b6d4 0%, #0d9488 100%);
          box-shadow: 0 8px 24px rgba(6,182,212,.38), inset 0 1px 0 rgba(255,255,255,.15);
          transition: all .22s; margin-top: 6px;
          position: relative; overflow: hidden;
        }
        .rg-submit::before {
          content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255,255,255,.2), transparent);
          transition: left .5s ease;
        }
        .rg-submit:hover:not(:disabled)::before { left: 100%; }
        .rg-submit:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 14px 36px rgba(6,182,212,.48), inset 0 1px 0 rgba(255,255,255,.15);
        }
        .rg-submit:active:not(:disabled) { transform: translateY(0); }
        .rg-submit:disabled { opacity: .6; cursor: not-allowed; }

        .rg-spin {
          display: inline-block; width: 15px; height: 15px;
          border: 2px solid rgba(255,255,255,.35); border-top-color: #fff;
          border-radius: 50%; animation: rgSpin .7s linear infinite;
          vertical-align: middle; margin-right: 7px;
        }
        @keyframes rgSpin { to { transform: rotate(360deg); } }

        .rg-or { display: flex; align-items: center; gap: 12px; margin: 16px 0; }
        .rg-orl { flex: 1; height: 1px; background: linear-gradient(90deg, transparent, #e2e8f0, transparent); }
        .rg-ort { font-size: 12px; color: #94a3b8; font-weight: 600; white-space: nowrap; }

        .rg-loginbtn {
          width: 100%; padding: 13px; border-radius: 13px;
          border: 1.5px solid #e2e8f0; background: white;
          cursor: pointer; font-family: 'Outfit', sans-serif;
          font-size: 14px; font-weight: 600; color: #374151;
          display: flex; align-items: center; justify-content: center; gap: 9px;
          transition: all .22s; text-decoration: none;
          box-shadow: 0 2px 8px rgba(0,0,0,.04);
        }
        .rg-loginbtn:hover {
          border-color: #06b6d4; background: #f0fdfe;
          color: #0891b2; transform: translateY(-1px);
          box-shadow: 0 6px 20px rgba(6,182,212,.12);
        }

        .rg-trust {
          display: flex; align-items: center; justify-content: center;
          gap: 6px; margin-top: 20px; padding-top: 18px;
          border-top: 1px solid #f1f5f9; flex-wrap: wrap;
          opacity: 0; transform: translateY(10px);
          animation: rgUp .6s ease forwards .72s;
        }
        .rg-ti {
          display: flex; align-items: center; gap: 4px;
          font-size: 11px; color: #94a3b8; font-weight: 600;
          padding: 4px 10px; border-radius: 100px;
          background: rgba(6,182,212,.05); border: 1px solid rgba(6,182,212,.1);
        }

        @keyframes rgUp { to { opacity: 1; transform: translateY(0); } }
      `}</style>

      <div className="rg-root">
        <div className="rg-blobs">
          <div className="rg-blob rg-b1"/>
          <div className="rg-blob rg-b2"/>
          <div className="rg-blob rg-b3"/>
        </div>
        <div className="rg-dotgrid"/>

        <div className="rg-card">
          <div className="rg-deco"/>

          <div className="rg-logorow">
            <img src={logo} alt="AIMHHC Logo" className="rg-logoimg" />
            <span className="rg-logotext">AI<span>MH</span>HC</span>
          </div>

          <div className="rg-head">
            <div className="rg-ctag">Create Account</div>
            <h2 className="rg-ctitle">Start your journey ✨</h2>
            <p className="rg-csub">Free, anonymous &amp; always private</p>
          </div>

          {error && (
            <div className="rg-err">⚠️ <span>{String(error)}</span></div>
          )}

          <form className="rg-form" onSubmit={handleRegister}>
            <div className="rg-field">
              <label>Full Name</label>
              <div className="rg-iw">
                <span className="rg-iico">🙍</span>
                <input type="text" placeholder="John Doe" value={form.fullName}
                  onChange={e => setForm({...form, fullName: e.target.value})} required autoComplete="name"/>
              </div>
            </div>

            <div className="rg-field">
              <label>Username</label>
              <div className="rg-iw">
                <span className="rg-iico">👤</span>
                <input type="text" placeholder="johndoe123" value={form.username}
                  onChange={e => setForm({...form, username: e.target.value})} required autoComplete="username"/>
              </div>
            </div>

            <div className="rg-field">
              <label>Email Address</label>
              <div className="rg-iw">
                <span className="rg-iico">📧</span>
                <input type="email" placeholder="name@example.com" value={form.email}
                  onChange={e => setForm({...form, email: e.target.value})} required autoComplete="email"/>
              </div>
            </div>

            <div className="rg-field">
              <label>Password</label>
              <div className="rg-iw">
                <span className="rg-iico">🔒</span>
                <input type={showPass ? 'text' : 'password'} placeholder="Create a strong password"
                  value={form.password} onChange={e => setForm({...form, password: e.target.value})}
                  required autoComplete="new-password"/>
                <button type="button" className="rg-eye" onClick={() => setShowPass(!showPass)}>
                  {showPass ? '🙈' : '👁️'}
                </button>
              </div>
            </div>

            <button type="submit" className="rg-submit" disabled={loading}>
              {loading ? <><span className="rg-spin"/>Creating Account...</> : 'Create Account →'}
            </button>
          </form>

          <div className="rg-or">
            <div className="rg-orl"/>
            <span className="rg-ort">Already have an account?</span>
            <div className="rg-orl"/>
          </div>

          <Link to="/login" className="rg-loginbtn">🔑 Sign In Instead</Link>

          <div className="rg-trust">
            <div className="rg-ti">🔒 SSL Secured</div>
            <div className="rg-ti">🛡️ Private</div>
            <div className="rg-ti">✨ No Ads</div>
            <div className="rg-ti">💚 Non-diagnostic</div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Register;