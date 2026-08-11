import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { toast } from 'sonner';
import { api, formatApiError } from '../../lib/api';

export default function AdminLogin() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [pendingToken, setPendingToken] = useState(null);
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const submitPassword = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const { data } = await api.post('/auth/login', { email, password });
      if (data.requires_2fa) {
        setPendingToken(data.pending_token);
      } else {
        navigate('/admin');
      }
    } catch (err) {
      toast.error(formatApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const submitCode = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/auth/2fa/verify', { pending_token: pendingToken, code });
      navigate('/admin');
    } catch (err) {
      toast.error(formatApiError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-auth" data-testid="admin-login-page">
      {pendingToken ? (
        <form className="admin-auth-card clipped" onSubmit={submitCode} data-testid="twofa-login-form">
          <p className="eyebrow accent">TWO-FACTOR CHECK</p>
          <h1>Enter your code</h1>
          <p className="muted auth-note">Open your authenticator app and enter the 6-digit code for AR ELECTRO Projects.</p>
          <label>Authentication code<input inputMode="numeric" autoComplete="one-time-code" required minLength="6" maxLength="6" value={code} onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))} data-testid="twofa-code-input" placeholder="000000" /></label>
          <button className="btn btn-primary form-submit" disabled={loading || code.length !== 6} data-testid="twofa-verify-submit">
            <span>{loading ? 'Verifying...' : 'Verify & sign in'}</span>
          </button>
          <button type="button" className="text-link" onClick={() => { setPendingToken(null); setCode(''); }} data-testid="twofa-back-button">Back to password</button>
        </form>
      ) : (
        <form className="admin-auth-card clipped" onSubmit={submitPassword}>
          <p className="eyebrow accent">AR ELECTRO PROJECTS / ADMIN</p>
          <h1>Studio access</h1>
          <label>Email<input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} data-testid="admin-email-input" placeholder="admin email" /></label>
          <label>Password<input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} data-testid="admin-password-input" placeholder="password" /></label>
          <button className="btn btn-primary form-submit" disabled={loading} data-testid="admin-login-submit">
            <span>{loading ? 'Signing in...' : 'Sign in'}</span>
          </button>
          <Link to="/" className="text-link" data-testid="admin-back-home-link">Back to site</Link>
        </form>
      )}
    </div>
  );
}
