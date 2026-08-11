import axios from 'axios';

const BASE = process.env.REACT_APP_BACKEND_URL;

export const api = axios.create({ baseURL: `${BASE}/api`, withCredentials: true });

export const resolveImage = (img) => {
  if (!img) return '';
  return img.startsWith('http') ? img : `${BASE}/api/files/${img}`;
};

export const extractVideoId = (input) => {
  const s = input.trim();
  const m = s.match(/(?:v=|youtu\.be\/|shorts\/|embed\/)([\w-]{11})/);
  return m ? m[1] : s;
};

export const WHATSAPP = 'https://wa.me/919998525347';
export const YOUTUBE_CHANNEL = 'https://youtube.com/@arelectroprojects';

export function formatApiError(err) {
  const detail = err?.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) return detail.map((e) => e?.msg || JSON.stringify(e)).join(' ');
  return err?.message || 'Something went wrong';
}
