import { Link } from 'react-router-dom';
import { ArrowUpRight } from 'lucide-react';
import { YOUTUBE_CHANNEL } from '../../lib/api';
import { Reveal } from './Reveal';

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        <Reveal className="footer-top">
          <div>
            <p className="eyebrow">AR ELECTRO PROJECTS / 2024—NOW</p>
            <h2 className="footer-cta">MAKE THE<br /><span>IDEA REAL.</span></h2>
          </div>
          <Link className="round-arrow" to="/contact" data-testid="footer-contact-link" aria-label="Go to contact">
            <ArrowUpRight size={30} />
          </Link>
        </Reveal>
        <div className="footer-bottom">
          <span data-testid="footer-gstin">GSTIN: 24DRWPA8036A1ZX</span>
          <span>AR ELECTRO PROJECTS ©</span>
          <div className="footer-links">
            <a href={YOUTUBE_CHANNEL} target="_blank" rel="noreferrer" data-testid="footer-youtube-link">YouTube</a>
            <a href="https://www.arelectroprojects.com/" target="_blank" rel="noreferrer" data-testid="footer-project-list-link">Project list</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
