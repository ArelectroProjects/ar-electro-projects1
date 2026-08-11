import { ArrowUpRight, Play } from 'lucide-react';
import { WHATSAPP, YOUTUBE_CHANNEL } from '../lib/api';
import { Reveal } from '../components/site/Reveal';

export default function About() {
  return (
    <section className="page container" data-testid="about-page">
      <Reveal>
        <p className="eyebrow accent">COMPANY PROFILE / EST. 2024</p>
        <h1 className="page-title">IDEAS IN.<br /><span>ENGINEERING OUT.</span></h1>
        <p className="page-intro">
          Welcome to AR ELECTRO Projects. We're dedicated to transforming ideas into reality through innovative
          technology projects — spreading knowledge and inspiring the next generation of thinkers and creators.
        </p>
      </Reveal>

      <div className="about-grid">
        <Reveal className="about-panel clipped" data-testid="about-founder-panel">
          <p className="eyebrow">FOUNDER</p>
          <h3>Postgraduate in Electrical Infrastructure</h3>
          <p>
            M.Tech in Electrical Infrastructure from the Institute of Infrastructure Technology Research and
            Management (IITRAM), Ahmedabad, Gujarat. A strong background in electrical engineering and innovation,
            now building cutting-edge engineering solutions for students and makers across India.
          </p>
        </Reveal>
        <Reveal className="about-panel clipped" delay={0.1} data-testid="about-offer-panel">
          <p className="eyebrow">WHAT WE OFFER</p>
          <ul className="offer-list">
            <li>Electrical &amp; Electronics Engineering Projects</li>
            <li>Mechanical Engineering Projects</li>
            <li>Arduino &amp; Microcontroller-Based Projects</li>
            <li>Drone Projects</li>
            <li>Custom project development</li>
            <li>Comprehensive after-sales support</li>
          </ul>
        </Reveal>
        <Reveal className="about-panel clipped" delay={0.15} data-testid="about-promise-panel">
          <p className="eyebrow">THE PROMISE</p>
          <h3>High quality. Competitive prices. Free all-India delivery.</h3>
          <p>
            Every build is engineered for Degree and Diploma students, tailored to your requirements,
            and supported until your project is presented with confidence.
          </p>
          <p className="gstin" data-testid="about-gstin">GSTIN: 24DRWPA8036A1ZX</p>
        </Reveal>
      </div>

      <Reveal className="about-actions">
        <a className="btn btn-primary" href={WHATSAPP} target="_blank" rel="noreferrer" data-testid="about-whatsapp-button">
          <span>Contact on WhatsApp</span> <ArrowUpRight size={17} />
        </a>
        <a className="text-link" href={YOUTUBE_CHANNEL} target="_blank" rel="noreferrer" data-testid="about-youtube-link">
          <Play size={15} fill="currentColor" /> Watch our builds on YouTube
        </a>
      </Reveal>
    </section>
  );
}
