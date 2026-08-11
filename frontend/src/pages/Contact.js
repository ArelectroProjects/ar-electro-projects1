import { useState } from 'react';
import { Mail, MapPin, Phone, Send } from 'lucide-react';
import { toast } from 'sonner';
import { api, formatApiError, WHATSAPP } from '../lib/api';
import { Reveal } from '../components/site/Reveal';

export default function Contact() {
  const [form, setForm] = useState({ name: '', email: '', phone: '', requirement: '' });
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/inquiries', form);
      toast.success('Requirement received — we’ll be in touch.');
      setForm({ name: '', email: '', phone: '', requirement: '' });
    } catch (err) {
      toast.error(formatApiError(err) || 'Could not send right now. Please use WhatsApp.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="page container contact" data-testid="contact-page">
      <Reveal className="contact-copy">
        <p className="eyebrow accent">CONTACT / LET’S BUILD</p>
        <h1 className="page-title">YOUR IDEA.<br /><span>OUR NEXT</span><br />PROJECT.</h1>
        <p className="page-intro">
          Tell us what you’re imagining. Share the rough version — we’ll help you find the right scope,
          components and path forward.
        </p>
        <div className="contact-lines">
          <a href={WHATSAPP} target="_blank" rel="noreferrer" data-testid="contact-whatsapp-link"><Phone size={18} /> +91 9998525347</a>
          <a href="mailto:arelectroprojects@gmail.com" data-testid="contact-email-link"><Mail size={18} /> arelectroprojects@gmail.com</a>
          <span><MapPin size={18} /> India / Supporting builders everywhere</span>
        </div>
      </Reveal>
      <Reveal delay={0.15}>
        <form className="contact-form clipped" onSubmit={submit} data-testid="contact-form">
          <label>Name<input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} data-testid="contact-name-input" placeholder="Your full name" /></label>
          <label>Email<input required type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} data-testid="contact-email-input" placeholder="you@example.com" /></label>
          <label>Phone<input required value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} data-testid="contact-phone-input" placeholder="+91 ..." /></label>
          <label>Project requirement<textarea required minLength="10" value={form.requirement} onChange={(e) => setForm({ ...form, requirement: e.target.value })} data-testid="contact-requirement-input" placeholder="Tell us about your idea, course and timeline..." /></label>
          <button className="btn btn-primary form-submit" disabled={loading} data-testid="contact-form-submit-button">
            <span>{loading ? 'Sending...' : 'Send requirement'}</span> <Send size={17} />
          </button>
        </form>
      </Reveal>
    </section>
  );
}
