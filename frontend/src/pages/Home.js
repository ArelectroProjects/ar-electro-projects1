import { useEffect, useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { motion, useScroll, useTransform } from 'framer-motion';
import { ArrowUpRight, ChevronRight, Play } from 'lucide-react';
import { api, resolveImage, WHATSAPP, YOUTUBE_CHANNEL } from '../lib/api';
import { Reveal, MaskedLine, Marquee } from '../components/site/Reveal';

const HERO_IMG = 'https://images.unsplash.com/photo-1604419623656-8ffddaae66b7?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85';

function Hero() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start start', 'end start'] });
  const imgY = useTransform(scrollYProgress, [0, 1], ['0%', '18%']);
  const imgScale = useTransform(scrollYProgress, [0, 1], [1, 1.12]);

  return (
    <section className="hero container" ref={ref}>
      <div className="hero-copy">
        <motion.p className="eyebrow accent" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.15, duration: 0.8 }}>
          AR ELECTRO PROJECTS — ENGINEERING ATELIER
        </motion.p>
        <h1 className="hero-title" data-testid="hero-title">
          <MaskedLine delay={0.25}>WE BUILD</MaskedLine>
          <MaskedLine delay={0.4} className="accent-line">WHAT YOU</MaskedLine>
          <MaskedLine delay={0.55}>IMAGINE.</MaskedLine>
        </h1>
        <motion.p className="hero-intro" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.85, duration: 0.8 }}>
          Transforming ideas into reality through innovative technology projects — and inspiring the next generation of thinkers and creators.
        </motion.p>
        <motion.div className="hero-actions" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1, duration: 0.8 }}>
          <Link className="btn btn-primary" to="/categories" data-testid="explore-projects-button">
            <span>Explore Projects</span> <ArrowUpRight size={18} />
          </Link>
          <a className="text-link" href={WHATSAPP} target="_blank" rel="noreferrer" data-testid="hero-whatsapp-link">
            Contact on WhatsApp <ChevronRight size={17} />
          </a>
        </motion.div>
      </div>
      <motion.div className="hero-feature" initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.5, duration: 1, ease: [0.22, 1, 0.36, 1] }}>
        <div className="feature-image clipped">
          <motion.img src={HERO_IMG} alt="Drone engineering project" style={{ y: imgY, scale: imgScale }} />
          <span className="feature-label">FEATURED / DRONE SYSTEMS</span>
        </div>
        <div className="feature-note">
          <span>500+</span>
          <p>PROJECTS<br />DELIVERED</p>
        </div>
      </motion.div>
    </section>
  );
}

function Manifesto() {
  const chapters = [
    { n: '01', t: 'LEARN', d: 'Every project ships with the knowledge behind it — reports, source code and viva support, so you truly own what you present.' },
    { n: '02', t: 'BUILD', d: 'From Arduino and microcontroller systems to drones and IoT — engineered, tested and delivered working, anywhere in India.' },
    { n: '03', t: 'LAUNCH', d: 'Ideas become final-year outcomes, portfolio pieces and real products. Your imagination sets the brief; we make it real.' },
  ];
  return (
    <section className="section container manifesto">
      <Reveal><p className="eyebrow accent">THE MANIFESTO</p></Reveal>
      {chapters.map((c, i) => (
        <Reveal key={c.n} delay={i * 0.08} className="chapter" data-testid={`manifesto-chapter-${c.n}`}>
          <span className="chapter-num">{c.n}</span>
          <h3 className="chapter-title">{c.t}</h3>
          <p className="chapter-desc">{c.d}</p>
        </Reveal>
      ))}
    </section>
  );
}

function CategoryIndex() {
  const [cats, setCats] = useState([]);
  useEffect(() => { api.get('/categories').then((r) => setCats(r.data)).catch(() => {}); }, []);
  return (
    <section className="section container" data-testid="category-index">
      <Reveal className="section-head">
        <div>
          <p className="eyebrow accent">THE INDEX</p>
          <h2 className="section-title">CHOOSE YOUR<br /><span>BUILD.</span></h2>
        </div>
        <Link className="text-link" to="/categories" data-testid="view-all-categories-link">View all categories <ArrowUpRight size={17} /></Link>
      </Reveal>
      <div className="project-grid">
        {cats.map((p, i) => (
          <Reveal key={p.slug} delay={(i % 3) * 0.08}>
            <Link to={`/projects/${p.slug}`} className="project-card" data-testid={`project-card-${p.slug}`}>
              <div className="project-image clipped">
                <img src={resolveImage(p.image)} alt={`${p.title} project`} loading={i < 3 ? 'eager' : 'lazy'} />
                <span className="card-index">{String(i + 1).padStart(2, '0')}</span>
                <span className="card-arrow"><ArrowUpRight size={19} /></span>
              </div>
              <div className="card-copy">
                <p className="eyebrow">{p.eyebrow}</p>
                <h3>{p.title}</h3>
                <p>{p.desc}</p>
              </div>
            </Link>
          </Reveal>
        ))}
      </div>
    </section>
  );
}

function Transmissions() {
  const [videos, setVideos] = useState([]);
  useEffect(() => { api.get('/videos').then((r) => setVideos(r.data)).catch(() => {}); }, []);
  return (
    <section className="section container" data-testid="youtube-showcase">
      <Reveal className="section-head">
        <div>
          <p className="eyebrow accent"><Play size={13} fill="currentColor" /> TRANSMISSIONS</p>
          <h2 className="section-title">PROJECTS THAT<br /><span>TEACH.</span></h2>
        </div>
        <a className="btn btn-outline" href={YOUTUBE_CHANNEL} target="_blank" rel="noreferrer" data-testid="youtube-channel-button">
          <span>Visit YouTube</span> <ArrowUpRight size={17} />
        </a>
      </Reveal>
      <div className="video-grid">
        {videos.map((v, i) => (
          <Reveal key={v.id || v.video_id} delay={i * 0.1} className="video-card" data-testid={`video-card-${i}`}>
            <div className="video-frame clipped">
              <iframe
                src={`https://www.youtube-nocookie.com/embed/${v.video_id}`}
                title={v.title}
                loading="lazy"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </div>
            <p className="video-title">{v.title}</p>
          </Reveal>
        ))}
      </div>
    </section>
  );
}

export default function Home() {
  return (
    <>
      <Hero />
      <Marquee items={['DIPLOMA', 'DEGREE', 'DRONE', 'ELECTRONICS', 'ELECTRICAL', 'EMBEDDED', 'MECHANICAL', 'BIOMEDICAL', 'IOT']} />
      <Manifesto />
      <CategoryIndex />
      <Transmissions />
    </>
  );
}
