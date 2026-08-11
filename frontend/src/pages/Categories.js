import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowUpRight } from 'lucide-react';
import { api, resolveImage } from '../lib/api';
import { Reveal } from '../components/site/Reveal';

export default function Categories() {
  const [cats, setCats] = useState([]);
  useEffect(() => { api.get('/categories').then((r) => setCats(r.data)).catch(() => {}); }, []);

  return (
    <section className="page container" data-testid="categories-page">
      <Reveal>
        <p className="eyebrow accent">PROJECT INDEX / 09 DISCIPLINES</p>
        <h1 className="page-title">EVERY BUILD,<br /><span>CATALOGUED.</span></h1>
        <p className="page-intro">Pick a discipline. Every category holds working projects with documentation, mentoring and after-sales support — delivered free across India.</p>
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
                <div className="tag-row">{(p.tags || []).map((t) => <span key={t} className="tag">{t}</span>)}</div>
              </div>
            </Link>
          </Reveal>
        ))}
      </div>
    </section>
  );
}
