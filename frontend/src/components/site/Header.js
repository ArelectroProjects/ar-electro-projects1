import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowUpRight, Menu, X } from 'lucide-react';
import { WHATSAPP } from '../../lib/api';

export default function Header() {
  const [open, setOpen] = useState(false);
  return (
    <header className="site-header">
      <div className="container header-inner">
        <Link to="/" className="brand" data-testid="brand-home-link">
          <span className="brand-mark">AR</span>
          <span className="brand-word">Electro<br /><b>Projects</b></span>
        </Link>
        <button className="menu-btn" onClick={() => setOpen(!open)} data-testid="mobile-menu-button" aria-label="Toggle menu">
          {open ? <X /> : <Menu />}
        </button>
        <nav className={open ? 'nav open' : 'nav'}>
          <Link to="/categories" data-testid="nav-categories-link" onClick={() => setOpen(false)}>Projects</Link>
          <Link to="/about" data-testid="nav-about-link" onClick={() => setOpen(false)}>About</Link>
          <Link to="/contact" data-testid="nav-contact-link" onClick={() => setOpen(false)}>Contact</Link>
          <a className="nav-whatsapp" href={WHATSAPP} target="_blank" rel="noreferrer" data-testid="nav-whatsapp-link">
            WhatsApp <ArrowUpRight size={15} />
          </a>
        </nav>
      </div>
    </header>
  );
}
