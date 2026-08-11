import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { LogOut, Trash2, Upload, Plus, Pencil, XCircle } from 'lucide-react';
import { toast } from 'sonner';
import { api, resolveImage, extractVideoId, formatApiError } from '../../lib/api';

function ImageUpload({ onUploaded, testId }) {
  const [busy, setBusy] = useState(false);
  const inputRef = useRef(null);
  const pick = () => inputRef.current?.click();
  const handle = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true);
    try {
      const data = new FormData();
      data.append('file', file);
      const res = await api.post('/admin/upload', data);
      onUploaded(res.data.path);
      toast.success('Photo uploaded');
    } catch (err) {
      toast.error(formatApiError(err));
    } finally {
      setBusy(false);
      e.target.value = '';
    }
  };
  return (
    <>
      <input ref={inputRef} type="file" accept="image/*" hidden onChange={handle} />
      <button type="button" className="btn btn-outline btn-sm" onClick={pick} disabled={busy} data-testid={testId}>
        <Upload size={15} /> <span>{busy ? 'Uploading...' : 'Upload photo'}</span>
      </button>
    </>
  );
}

function InquiriesTab() {
  const [items, setItems] = useState([]);
  useEffect(() => { api.get('/inquiries').then((r) => setItems(r.data)).catch(() => {}); }, []);
  return (
    <div data-testid="admin-inquiries-tab">
      {items.length === 0 && <p className="muted">No enquiries yet.</p>}
      {items.map((q, i) => (
        <div className="admin-row" key={q.id} data-testid={`inquiry-row-${i}`}>
          <div>
            <b>{q.name}</b>
            <p className="muted">{q.email} · {q.phone}</p>
            <p>{q.requirement}</p>
          </div>
          <span className="muted row-date">{new Date(q.created_at).toLocaleDateString('en-IN')}</span>
        </div>
      ))}
    </div>
  );
}

function ProjectsTab() {
  const [cats, setCats] = useState([]);
  const [projects, setProjects] = useState([]);
  const [form, setForm] = useState({ category: 'diploma-project', title: '', description: '', price_hint: '', image: '' });
  const [busy, setBusy] = useState(false);
  const [editingId, setEditingId] = useState(null);

  const load = useCallback(() => {
    api.get('/categories').then((r) => setCats(r.data)).catch(() => {});
    api.get('/projects').then((r) => setProjects(r.data)).catch(() => {});
  }, []);
  useEffect(() => { load(); }, [load]);

  const resetForm = () => {
    setForm({ category: 'diploma-project', title: '', description: '', price_hint: '', image: '' });
    setEditingId(null);
  };

  const save = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      if (editingId) {
        await api.put(`/admin/projects/${editingId}`, form);
        toast.success('Project updated');
      } else {
        await api.post('/admin/projects', form);
        toast.success('Project added');
      }
      resetForm();
      load();
    } catch (err) {
      toast.error(formatApiError(err));
    } finally {
      setBusy(false);
    }
  };

  const startEdit = (p) => {
    setEditingId(p.id);
    setForm({ category: p.category, title: p.title, description: p.description, price_hint: p.price_hint || '', image: p.image || '' });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const remove = async (id) => {
    try {
      await api.delete(`/admin/projects/${id}`);
      toast.success('Project deleted');
      load();
    } catch (err) {
      toast.error(formatApiError(err));
    }
  };

  return (
    <div data-testid="admin-projects-tab">
      <form className="admin-form clipped" onSubmit={save}>
        {editingId && (
          <div className="edit-banner" data-testid="edit-mode-banner">
            <span>Editing project — changes save over the existing listing</span>
            <button type="button" className="icon-btn" onClick={resetForm} data-testid="cancel-edit-button" aria-label="Cancel edit"><XCircle size={16} /></button>
          </div>
        )}
        <div className="admin-form-grid">
          <label>Category
            <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} data-testid="project-category-select">
              {cats.map((c) => <option key={c.slug} value={c.slug}>{c.title}</option>)}
            </select>
          </label>
          <label>Title<input required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} data-testid="project-title-input" placeholder="e.g. Smart Energy Meter" /></label>
          <label>Price hint<input value={form.price_hint} onChange={(e) => setForm({ ...form, price_hint: e.target.value })} data-testid="project-price-input" placeholder="e.g. ₹2,999 onwards" /></label>
        </div>
        <label>Description<textarea required minLength="5" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} data-testid="project-description-input" placeholder="One or two lines about the build" /></label>
        <div className="admin-form-actions">
          <ImageUpload testId="project-image-upload-button" onUploaded={(path) => setForm({ ...form, image: path })} />
          {form.image && <img className="admin-preview clipped" src={resolveImage(form.image)} alt="project" data-testid="project-image-preview" />}
          <button className="btn btn-primary btn-sm" disabled={busy} data-testid="project-add-submit"><Plus size={15} /> <span>{busy ? 'Saving...' : editingId ? 'Update project' : 'Add project'}</span></button>
        </div>
      </form>
      {projects.map((p, i) => (
        <div className="admin-row" key={p.id} data-testid={`admin-project-row-${i}`}>
          {p.image && <img className="admin-thumb clipped" src={resolveImage(p.image)} alt={p.title} />}
          <div>
            <b>{p.title}</b>
            <p className="muted">{p.category} {p.price_hint ? `· ${p.price_hint}` : ''}</p>
          </div>
          <button className="icon-btn" onClick={() => startEdit(p)} data-testid={`project-edit-${i}`} aria-label="Edit project"><Pencil size={16} /></button>
          <button className="icon-btn" onClick={() => remove(p.id)} data-testid={`project-delete-${i}`} aria-label="Delete project"><Trash2 size={16} /></button>
        </div>
      ))}
    </div>
  );
}

function CategoriesTab() {
  const [cats, setCats] = useState([]);
  const load = useCallback(() => { api.get('/categories').then((r) => setCats(r.data)).catch(() => {}); }, []);
  useEffect(() => { load(); }, [load]);

  const setImage = async (slug, path) => {
    try {
      await api.put(`/admin/categories/${slug}`, { image: path });
      toast.success('Category photo updated');
      load();
    } catch (err) {
      toast.error(formatApiError(err));
    }
  };

  return (
    <div className="admin-cat-grid" data-testid="admin-categories-tab">
      {cats.map((c, i) => (
        <div className="admin-cat-card clipped" key={c.slug} data-testid={`admin-category-${c.slug}`}>
          <img src={resolveImage(c.image)} alt={c.title} />
          <div className="admin-cat-body">
            <b>{c.title}</b>
            <ImageUpload testId={`category-upload-${i}`} onUploaded={(path) => setImage(c.slug, path)} />
          </div>
        </div>
      ))}
    </div>
  );
}

function VideosTab() {
  const [videos, setVideos] = useState([]);
  const [url, setUrl] = useState('');
  const [title, setTitle] = useState('');
  const load = useCallback(() => { api.get('/videos').then((r) => setVideos(r.data)).catch(() => {}); }, []);
  useEffect(() => { load(); }, [load]);

  const add = async (e) => {
    e.preventDefault();
    try {
      await api.post('/admin/videos', { video_id: extractVideoId(url), title });
      toast.success('Video added');
      setUrl(''); setTitle('');
      load();
    } catch (err) {
      toast.error(formatApiError(err));
    }
  };

  const remove = async (id) => {
    try {
      await api.delete(`/admin/videos/${id}`);
      toast.success('Video removed');
      load();
    } catch (err) {
      toast.error(formatApiError(err));
    }
  };

  return (
    <div data-testid="admin-videos-tab">
      <form className="admin-form clipped" onSubmit={add}>
        <div className="admin-form-grid">
          <label>YouTube link<input required value={url} onChange={(e) => setUrl(e.target.value)} data-testid="video-url-input" placeholder="https://youtube.com/watch?v=..." /></label>
          <label>Title<input required value={title} onChange={(e) => setTitle(e.target.value)} data-testid="video-title-input" placeholder="e.g. GSM Gas Leak Detector" /></label>
        </div>
        <div className="admin-form-actions">
          <button className="btn btn-primary btn-sm" data-testid="video-add-submit"><Plus size={15} /> <span>Add video</span></button>
        </div>
      </form>
      {videos.map((v, i) => (
        <div className="admin-row" key={v.id} data-testid={`admin-video-row-${i}`}>
          <img className="admin-thumb clipped" src={`https://i.ytimg.com/vi/${v.video_id}/default.jpg`} alt={v.title} />
          <div>
            <b>{v.title}</b>
            <p className="muted">youtube.com/watch?v={v.video_id}</p>
          </div>
          <button className="icon-btn" onClick={() => remove(v.id)} data-testid={`video-delete-${i}`} aria-label="Delete video"><Trash2 size={16} /></button>
        </div>
      ))}
    </div>
  );
}

const TABS = [
  { key: 'inquiries', label: 'Enquiries', Comp: InquiriesTab },
  { key: 'projects', label: 'Projects', Comp: ProjectsTab },
  { key: 'categories', label: 'Category Photos', Comp: CategoriesTab },
  { key: 'videos', label: 'YouTube Videos', Comp: VideosTab },
];

export default function AdminDashboard() {
  const [user, setUser] = useState(null);
  const [tab, setTab] = useState('inquiries');
  const navigate = useNavigate();

  useEffect(() => {
    api.get('/auth/me')
      .then((r) => setUser(r.data))
      .catch(() => navigate('/admin/login'));
  }, [navigate]);

  const logout = async () => {
    await api.post('/auth/logout').catch(() => {});
    navigate('/admin/login');
  };

  if (!user) return <div className="admin-auth"><p className="eyebrow">CHECKING ACCESS…</p></div>;

  const Active = TABS.find((t) => t.key === tab).Comp;

  return (
    <div className="admin-shell" data-testid="admin-dashboard">
      <header className="admin-head">
        <div>
          <p className="eyebrow accent">AR ELECTRO PROJECTS / STUDIO</p>
          <h1>Dashboard</h1>
        </div>
        <div className="admin-head-actions">
          <Link to="/" className="text-link" data-testid="admin-view-site-link">View site</Link>
          <button className="btn btn-outline btn-sm" onClick={logout} data-testid="admin-logout-button"><LogOut size={15} /> <span>Log out</span></button>
        </div>
      </header>
      <nav className="admin-tabs">
        {TABS.map((t) => (
          <button key={t.key} className={tab === t.key ? 'admin-tab active' : 'admin-tab'} onClick={() => setTab(t.key)} data-testid={`admin-tab-${t.key}`}>
            {t.label}
          </button>
        ))}
      </nav>
      <Active />
    </div>
  );
}
