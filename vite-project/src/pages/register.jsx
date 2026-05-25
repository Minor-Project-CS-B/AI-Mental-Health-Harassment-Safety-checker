import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { sendOTP, verifyOTP, googleAuth } from '../services/api'; // Added googleAuth import
import logo from '../assets/logo minor.jpg';

const Register = () => {
  const navigate = useNavigate();

  // step: 'form' | 'otp' | 'success'
  const [step, setStep]       = useState('form');
  const [form, setForm]       = useState({ fullName: '', username: '', email: '', password: '' });
  const [otp, setOtp]         = useState('');
  const [error, setError]     = useState('');
  const [loading, setLoading] = useState(false);
  const [showPass, setShowPass] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);

  // ── Google Register/Login handler ─────────────────────────────────────────
  const handleGoogleRegister = async (response) => {
    setLoading(true);
    setError('');
    try {
      const res = await googleAuth(response.credential);
      const d   = res.data;
      if (d.status === 'logged_in') {
        // Already had account — just log them in
        localStorage.setItem('token', d.access_token);
        navigate('/dashboard');
      } else if (d.status === 'needs_profile') {
        // New user — complete profile
        const params = new URLSearchParams({
          google_id: d.google_id,
          email:     d.email,
          name:      encodeURIComponent(d.name || ''),
        });
        navigate(`/complete-profile?${params.toString()}`);
      }
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Google sign-in failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };
 
  // Load Google Identity Services and render button
  useEffect(() => {
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
    if (!clientId) {
      console.warn('VITE_GOOGLE_CLIENT_ID not set in .env file');
      return;
    }
 
    const renderGoogleBtn = () => {
      const el = document.getElementById('google-btn-register');
      if (!el || !window.google?.accounts?.id) return;
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback:  handleGoogleRegister,
      });
      window.google.accounts.id.renderButton(el, {
        theme: 'outline',
        size:  'large',
        width: 360,
        text:  'signup_with',
        logo_alignment: 'center',
      });
    };
 
    // If SDK already loaded (e.g. navigated back to page)
    if (window.google?.accounts?.id) {
      renderGoogleBtn();
      return;
    }
 
    // Otherwise load the script
    const existing = document.getElementById('google-gsi-script');
    if (!existing) {
      const script  = document.createElement('script');
      script.id     = 'google-gsi-script';
      script.src    = 'https://accounts.google.com/gsi/client';
      script.async  = true;
      script.defer  = true;
      script.onload = renderGoogleBtn;
      document.head.appendChild(script);
    } else {
      // Script tag exists but onload already fired — just render
      setTimeout(renderGoogleBtn, 100);
    }
  }, []);

  // ── Step 1: Validate email + send OTP ─────────────────────────────────────
  const handleSendOTP = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await sendOTP({
        name:     form.fullName,
        username: form.username,
        email:    form.email,
        password: form.password,
      });
      setStep('otp');
      startResendCooldown();
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // ── Step 2: Verify OTP + create account ────────────────────────────────────
  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    if (otp.length !== 6) { setError('Please enter the complete 6-digit code.'); return; }
    setLoading(true);
    setError('');
    try {
      await verifyOTP({
        email:    form.email,
        otp:      otp.trim(),
        name:     form.fullName,
        username: form.username,
        password: form.password,
      });
      setStep('success');
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Verification failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // ── Resend OTP with 60s cooldown ──────────────────────────────────────────
  const startResendCooldown = () => {
    setResendCooldown(60);
    const interval = setInterval(() => {
      setResendCooldown(prev => {
        if (prev <= 1) { clearInterval(interval); return 0; }
        return prev - 1;
      });
    }, 1000);
  };

  const handleResend = async () => {
    if (resendCooldown > 0) return;
    setLoading(true);
    setError('');
    try {
      await sendOTP({ name: form.fullName, username: form.username, email: form.email, password: form.password });
      setOtp('');
      startResendCooldown();
    } catch (err) {
      setError('Could not resend code. Please try again.');
    } finally { setLoading(false); }
  };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');
        .rg-root*{box-sizing:border-box}
        .rg-root{min-height:100vh;display:flex;align-items:center;justify-content:center;font-family:'Outfit',sans-serif;background:linear-gradient(135deg,#f0fdfb 0%,#e0f7fa 40%,#f0fdfa 70%,#ecfdf5 100%);position:relative;overflow:hidden;padding:24px}
        .rg-blobs{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
        .rg-blob{position:absolute;border-radius:50%;animation:rgDrift 14s ease-in-out infinite alternate}
        .rg-b1{width:520px;height:520px;background:radial-gradient(circle,rgba(6,182,212,.18),rgba(20,184,166,.06));top:-120px;left:-80px}
        .rg-b2{width:400px;height:400px;background:radial-gradient(circle,rgba(20,184,166,.16),rgba(6,182,212,.05));bottom:-80px;right:-60px;animation-delay:-5s}
        .rg-b3{width:280px;height:280px;background:radial-gradient(circle,rgba(6,182,212,.1),transparent);top:45%;left:48%;animation-delay:-9s}
        @keyframes rgDrift{0%{transform:translate(0,0) scale(1)}50%{transform:translate(30px,-25px) scale(1.07)}100%{transform:translate(-15px,20px) scale(.96)}}
        .rg-dotgrid{position:fixed;inset:0;z-index:0;pointer-events:none;background-image:radial-gradient(circle,rgba(6,182,212,.15) 1px,transparent 1px);background-size:28px 28px;opacity:.6}
        .rg-card{position:relative;z-index:1;width:100%;max-width:460px;background:rgba(255,255,255,.75);backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);border:1.5px solid rgba(6,182,212,.15);border-radius:28px;padding:40px;box-shadow:0 0 0 1px rgba(6,182,212,.06),0 24px 64px rgba(6,182,212,.13),0 4px 16px rgba(0,0,0,.05);opacity:0;transform:translateY(28px);animation:rgUp .75s cubic-bezier(.16,1,.3,1) forwards .15s}
        .rg-deco{width:100%;height:4px;border-radius:100px;background:linear-gradient(90deg,#06b6d4,#14b8a6,#06b6d4);background-size:200% 100%;animation:rgShimmer 3s linear infinite;margin-bottom:28px}
        @keyframes rgShimmer{0%{background-position:0% 0}100%{background-position:200% 0}}
        .rg-logorow{display:flex;align-items:center;gap:12px;justify-content:center;margin-bottom:20px}
        .rg-logoimg{width:48px;height:48px;border-radius:14px;object-fit:contain;background:white;padding:4px;box-shadow:0 8px 20px rgba(6,182,212,.25)}
        .rg-logotext{font-size:20px;font-weight:800;color:#0f172a;letter-spacing:-.02em}
        .rg-logotext span{background:linear-gradient(135deg,#06b6d4,#0d9488);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
        .rg-head{text-align:center;margin-bottom:24px}
        .rg-ctag{display:inline-block;font-size:11px;font-weight:700;color:#0891b2;background:rgba(6,182,212,.09);border:1px solid rgba(6,182,212,.2);padding:4px 12px;border-radius:100px;text-transform:uppercase;letter-spacing:.07em;margin-bottom:10px}
        .rg-ctitle{font-size:24px;font-weight:800;color:#0f172a;letter-spacing:-.02em;line-height:1.2}
        .rg-csub{font-size:13.5px;color:#94a3b8;margin-top:5px}
        .rg-field{margin-bottom:15px}
        .rg-field label{display:block;font-size:12px;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:.07em;margin-bottom:8px}
        .rg-iw{position:relative}
        .rg-iico{position:absolute;left:14px;top:50%;transform:translateY(-50%);font-size:15px;opacity:.4;pointer-events:none}
        .rg-field input{width:100%;padding:12px 14px 12px 42px;border-radius:13px;border:1.5px solid #e2e8f0;background:#f8fafc;color:#0f172a;font-family:'Outfit',sans-serif;font-size:14.5px;outline:none;transition:all .22s ease}
        .rg-field input::placeholder{color:#cbd5e1}
        .rg-field input:focus{border-color:#06b6d4;background:#f0fdfe;box-shadow:0 0 0 4px rgba(6,182,212,.1)}
        .rg-eye{position:absolute;right:12px;top:50%;transform:translateY(-50%);background:none;border:none;cursor:pointer;font-size:15px;opacity:.4;padding:4px;border-radius:6px;transition:opacity .2s}
        .rg-eye:hover{opacity:.8}
        .rg-err{background:#fef2f2;border:1.5px solid #fecaca;border-radius:12px;padding:11px 14px;font-size:13px;color:#dc2626;display:flex;align-items:center;gap:8px;margin-bottom:14px}
        .rg-success{background:#f0fdf4;border:1.5px solid #bbf7d0;border-radius:16px;padding:24px;text-align:center;margin-bottom:16px}
        .rg-submit{width:100%;padding:14px;border-radius:13px;border:none;cursor:pointer;font-family:'Outfit',sans-serif;font-size:15px;font-weight:700;color:#fff;background:linear-gradient(135deg,#06b6d4 0%,#0d9488 100%);box-shadow:0 8px 24px rgba(6,182,212,.38);transition:all .22s;margin-top:6px}
        .rg-submit:hover:not(:disabled){transform:translateY(-2px);box-shadow:0 14px 36px rgba(6,182,212,.48)}
        .rg-submit:disabled{opacity:.6;cursor:not-allowed}
        .rg-spin{display:inline-block;width:15px;height:15px;border:2px solid rgba(255,255,255,.35);border-top-color:#fff;border-radius:50%;animation:rgSpin .7s linear infinite;vertical-align:middle;margin-right:7px}
        @keyframes rgSpin{to{transform:rotate(360deg)}}
        .rg-back{background:none;border:none;color:#64748b;font-size:13px;font-weight:600;cursor:pointer;display:flex;align-items:center;gap:4px;margin-bottom:16px;padding:0;font-family:'Outfit',sans-serif}
        .rg-back:hover{color:#0891b2}
        .rg-resend{font-size:13px;color:#94a3b8;text-align:center;margin-top:14px}
        .rg-resend button{background:none;border:none;color:#0891b2;font-weight:700;cursor:pointer;font-family:'Outfit',sans-serif;font-size:13px}
        .rg-resend button:disabled{color:#cbd5e1;cursor:not-allowed}
        .rg-or{display:flex;align-items:center;gap:12px;margin:16px 0}
        .rg-orl{flex:1;height:1px;background:linear-gradient(90deg,transparent,#e2e8f0,transparent)}
        .rg-ort{font-size:12px;color:#94a3b8;font-weight:600;white-space:nowrap}
        .rg-loginbtn{width:100%;padding:13px;border-radius:13px;border:1.5px solid #e2e8f0;background:white;cursor:pointer;font-family:'Outfit',sans-serif;font-size:14px;font-weight:600;color:#374151;display:flex;align-items:center;justify-content:center;gap:9px;transition:all .22s;text-decoration:none;box-shadow:0 2px 8px rgba(0,0,0,.04)}
        .rg-loginbtn:hover{border-color:#06b6d4;background:#f0fdfe;color:#0891b2;transform:translateY(-1px)}
        .rg-trust{display:flex;align-items:center;justify-content:center;gap:6px;margin-top:20px;padding-top:18px;border-top:1px solid #f1f5f9;flex-wrap:wrap}
        .rg-ti{display:flex;align-items:center;gap:4px;font-size:11px;color:#94a3b8;font-weight:600;padding:4px 10px;border-radius:100px;background:rgba(6,182,212,.05);border:1px solid rgba(6,182,212,.1)}
        @keyframes rgUp{to{opacity:1;transform:translateY(0)}}
      `}</style>

      <div className="rg-root">
        <div className="rg-blobs"><div className="rg-blob rg-b1"/><div className="rg-blob rg-b2"/><div className="rg-blob rg-b3"/></div>
        <div className="rg-dotgrid"/>

        <div className="rg-card">
          <div className="rg-deco"/>
          <div className="rg-logorow">
            <img src={logo} alt="AIMHHC Logo" className="rg-logoimg"/>
            <span className="rg-logotext">AI<span>MH</span>HC</span>
          </div>

          {/* ── STEP 1: Registration Form ── */}
          {step === 'form' && (
            <>
              <div className="rg-head">
                <div className="rg-ctag">Create Account</div>
                <h2 className="rg-ctitle">Start your journey ✨</h2>
                <p className="rg-csub">Free, anonymous &amp; always private</p>
              </div>

              {/* Google Sign-Up button container */}
              <div style={{ marginBottom: 18 }}>
                <div id="google-btn-register" style={{ display: 'flex', justifyContent: 'center', minHeight: '44px' }}/>
              </div>
 
              <div className="rg-or">
                <div className="rg-orl"/>
                <span className="rg-ort">or register manually</span>
                <div className="rg-orl"/>
              </div>

              {error && <div className="rg-err">⚠️ <span>{error}</span></div>}

              <form onSubmit={handleSendOTP}>
                <div className="rg-field">
                  <label>Full Name</label>
                  <div className="rg-iw"><span className="rg-iico">🙍</span>
                    <input type="text" placeholder="John Doe" value={form.fullName}
                      onChange={e=>setForm({...form,fullName:e.target.value})} required autoComplete="name"/>
                  </div>
                </div>
                <div className="rg-field">
                  <label>Username</label>
                  <div className="rg-iw"><span className="rg-iico">👤</span>
                    <input type="text" placeholder="johndoe123" value={form.username}
                      onChange={e=>setForm({...form,username:e.target.value})} required autoComplete="username"/>
                  </div>
                </div>
                <div className="rg-field">
                  <label>Email Address</label>
                  <div className="rg-iw"><span className="rg-iico">📧</span>
                    <input type="email" placeholder="name@example.com" value={form.email}
                      onChange={e=>setForm({...form,email:e.target.value})} required autoComplete="email"/>
                  </div>
                </div>
                <div className="rg-field">
                  <label>Password</label>
                  <div className="rg-iw"><span className="rg-iico">🔒</span>
                    <input type={showPass?'text':'password'} placeholder="Create a strong password"
                      value={form.password} onChange={e=>setForm({...form,password:e.target.value})}
                      required autoComplete="new-password"/>
                    <button type="button" className="rg-eye" onClick={()=>setShowPass(!showPass)}>
                      {showPass?'🙈':'👁️'}
                    </button>
                  </div>
                </div>
                <button type="submit" className="rg-submit" disabled={loading}>
                  {loading ? <><span className="rg-spin"/>Validating email...</> : 'Send Verification Code →'}
                </button>
              </form>

              <div className="rg-or"><div className="rg-orl"/><span className="rg-ort">Already have an account?</span><div className="rg-orl"/></div>
              <Link to="/login" className="rg-loginbtn">🔑 Sign In Instead</Link>
            </>
          )}

          {/* ── STEP 2: OTP Entry ── */}
          {step === 'otp' && (
            <>
              <button className="rg-back" onClick={() => { setStep('form'); setError(''); setOtp(''); }}>
                ← Back
              </button>
              <div className="rg-head">
                <div className="rg-ctag">Verify Email</div>
                <h2 className="rg-ctitle">Check your inbox 📬</h2>
                <p className="rg-csub">
                  We sent a 6-digit code to<br/>
                  <strong style={{color:'#0891b2'}}>{form.email}</strong>
                </p>
              </div>

              {error && <div className="rg-err">⚠️ <span>{error}</span></div>}

              <form onSubmit={handleVerifyOTP}>
                <div className="rg-field">
                  <label style={{textAlign:'center',display:'block'}}>Enter 6-digit code</label>
                  <input
                    type="text"
                    inputMode="numeric"
                    maxLength={6}
                    placeholder="000000"
                    value={otp}
                    onChange={e => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    style={{
                      width:'100%', padding:'16px', borderRadius:14,
                      border:'2px solid #e2e8f0', background:'#f8fafc',
                      fontSize:32, fontWeight:800, textAlign:'center',
                      letterSpacing:14, fontFamily:"'Outfit', monospace",
                      outline:'none', transition:'all .2s', color:'#0f172a'
                    }}
                    onFocus={e => { e.target.style.borderColor='#06b6d4'; e.target.style.boxShadow='0 0 0 4px rgba(6,182,212,.1)'; }}
                    onBlur={e => { e.target.style.borderColor='#e2e8f0'; e.target.style.boxShadow='none'; }}
                    autoComplete="one-time-code"
                    autoFocus
                  />
                </div>

                <button type="submit" className="rg-submit" disabled={loading || otp.length < 6}>
                  {loading ? <><span className="rg-spin"/>Verifying...</> : 'Verify & Create Account →'}
                </button>
              </form>

              <div className="rg-resend">
                Didn't receive the code?{' '}
                <button onClick={handleResend} disabled={resendCooldown > 0 || loading}>
                  {resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend Code'}
                </button>
              </div>
            </>
          )}

          {/* ── STEP 3: Success ── */}
          {step === 'success' && (
            <div className="rg-success">
              <div style={{fontSize:40,marginBottom:10}}>✅</div>
              <p style={{fontSize:16,fontWeight:800,color:'#16a34a',margin:'0 0 8px'}}>
                Account Created!
              </p>
              <p style={{fontSize:13,color:'#4b5563',lineHeight:1.6,margin:'0 0 16px'}}>
                Your email is verified. Check <strong>{form.email}</strong> for your login link.
              </p>
              <Link to="/login" style={{display:'inline-block',padding:'10px 24px',borderRadius:12,background:'#16a34a',color:'white',fontWeight:700,fontSize:13,textDecoration:'none'}}>
                Go to Login →
              </Link>
            </div>
          )}

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