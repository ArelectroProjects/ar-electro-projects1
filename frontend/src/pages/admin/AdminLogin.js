import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { toast } from 'sonner';
import { api, formatApiError } from '../../lib/api';

export default function AdminLogin() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/auth/login', { email, password });
      navigate('/admin');
    } catch (err) {
      toast.error(formatApiError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-auth" data-testid="admin-login-page">
      <form className="admin-auth-card clipped" onSubmit={submit}>
        <p className="eyebrow accent">AR ELECTRO PROJECTS / ADMIN</p>
        <h1>Studio access</h1>
        <label>Email<input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} data-testid="admin-email-input" placeholder="admin email" /></label>
        <label>Password<input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} data-testid="admin-password-input" placeholder="password" /></label>
        <button className="btn btn-primary form-submit" disabled={loading} data-testid="admin-login-submit">
          <span>{loading ? 'Signing in...' : 'Sign in'}</span>
        </button>
        <Link to="/" className="text-link" data-testid="admin-back-home-link">Back to site</Link>
      </form>
    </div>
  );
}
