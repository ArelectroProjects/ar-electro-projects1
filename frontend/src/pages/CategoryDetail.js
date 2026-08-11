import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ArrowLeft, ArrowUpRight } from 'lucide-react';
import { api, resolveImage, WHATSAPP } from '../lib/api';
import { Reveal } from '../components/site/Reveal';

export default function CategoryDetail() {
  const { slug } = useParams();
  const [cat, setCat] = useState(null);
  const [projects, setProjects] = useState([]);

  useEffect(() => {
    api.get('/categories').then((r) => setCat(r.data.find((c) => c.slug === slug) || null)).catch(() => {});
    api.get(`/projects?category=${slug}`).then((r) => setProjects(r.data)).catch(() => {});
  }, [slug]);

  if (!cat) return <section className="page container"><p className="eyebrow">LOADING…</p></section>;

  const waText = encodeURIComponent(`Hi AR ELECTRO Projects, I'm interested in a ${cat.title}.`);

  return (
    <section className="page container" data-testid="category-detail-page">
      <Reveal>
        <Link to="/categories" className="text-link back-link" data-testid="back-to-categories-link"><ArrowLeft size={16} /> All categories</Link>
        <p className="eyebrow accent">{cat.eyebrow}</p>
        <h1 className="page-title">{cat.title.toUpperCase()}</h1>
        <p className="page-intro">{cat.desc}</p>
      </Reveal>
      {cat.image && (
        <Reveal className="detail-hero clipped">
          <img src={resolveImage(cat.image)} alt={`${cat.title} hero`} />
        </Reveal>
      )}
      <div className="listing-head">
        <p className="eyebrow">PROJECT LIST / {projects.length} BUILDS</p>
        <a className="btn btn-primary" href={`${WHATSAPP}?text=${waText}`} target="_blank" rel="noreferrer" data-testid="detail-whatsapp-button">
          <span>Request custom build</span> <ArrowUpRight size={17} />
        </a>
      </div>
      <div className="project-list">
        {projects.map((p, i) => (
          <Reveal key={p.id} delay={i * 0.05} className="project-row" data-testid={`project-row-${i}`}>
            <span className="row-index">{String(i + 1).padStart(2, '0')}</span>
            {p.image && <img className="row-thumb clipped" src={resolveImage(p.image)} alt={p.title} />}
            <div className="row-copy">
              <h3>{p.title}</h3>
              <p>{p.description}</p>
            </div>
            <div className="row-actions">
              {p.price_hint && <span className="price-chip" data-testid={`price-hint-${i}`}>{p.price_hint}</span>}
              <a
                className="enquire-btn"
                href={`${WHATSAPP}?text=${encodeURIComponent(`Hi AR ELECTRO Projects, I'm interested in the "${p.title}" (${cat.title}) project. Please share details and pricing.`)}`}
                target="_blank"
                rel="noreferrer"
                data-testid={`row-enquire-${i}`}
              >
                Enquire <ArrowUpRight size={14} />
              </a>
            </div>
          </Reveal>
        ))}
        {projects.length === 0 && <p className="muted">Projects for this category are being catalogued — message us on WhatsApp for the full list.</p>}
      </div>
    </section>
  );
}
