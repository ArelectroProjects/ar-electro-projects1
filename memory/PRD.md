# PRD — AR ELECTRO Projects Website

## Original Problem Statement
Website for "AR ELECTRO Projects" — multi-page site with About Us, project categories with photos (Diploma, Degree, Drone, Electronics, Electrical, Embedded, Mechanical, Biomedical, IoT), contact form. Theme: black + #e51a4D. CTAs: "Explore Projects", "Contact on WhatsApp". YouTube: youtube.com/@arelectroprojects. GSTIN 24DRWPA8036A1ZX. Reference: arelectroprojects.com.

## User Personas
- Diploma/Degree engineering students seeking final-year projects
- Makers wanting drones, IoT, embedded builds
- Owner (admin) managing photos, project listings, videos and enquiries

## Architecture
- Frontend: React + Tailwind + framer-motion (scroll reveals, masked hero reveal, parallax) + lenis (smooth scroll)
- Backend: FastAPI, routes under /api; JWT cookie auth for admin; Emergent object storage for uploads; Resend for enquiry email alerts
- DB: MongoDB — users, categories, projects, videos, inquiries, files, login_attempts
- Config: frontend/.env (REACT_APP_BACKEND_URL), backend/.env (MONGO_URL, DB_NAME, JWT_SECRET, ADMIN_EMAIL, ADMIN_PASSWORD, EMERGENT_LLM_KEY, ALERT_EMAIL, SENDER_EMAIL, APP_NAME)

## Implemented
### 2026-08-10 (initial)
- Multi-page site, black/#e51a4D theme, category grid, About, Contact form -> MongoDB
### 2026-08-11 (phase 2)
- Award-level redesign: kinetic masked-line hero, parallax spotlight image, editorial marquee, numbered manifesto chapters, clipped frames, grain overlay, Syne/IBM Plex Mono/Manrope type
- Theme flipped to white background + pink (#e51a4D) accents, black used sparingly (footer band, chips on photos) per client request
- Admin dashboard (/admin): JWT login, photo upload per category (object storage), project CRUD with price hints, YouTube video management, enquiry inbox
- Project listings: each category page shows individual builds with title, description, price hint (₹), seeded with 12 starter projects
- YouTube showcase: 3 real channel videos embedded on home (GSM Gas Leak Detector, Automatic Power Factor Correction, DIY Electric Cycle), admin-editable
- Enquiry alerts: email to arelectroprojects@gmail.com wired via Resend — ACTIVE only when RESEND_API_KEY is set (currently SKIPPED, key not provisioned); WhatsApp alerts NOT built (needs Twilio credentials)

## Credentials
- Admin: arelectroprojects@gmail.com / ARElectro@2026 (see /app/memory/test_credentials.md)

## Backlog
- P0: Activate email alerts (provision RESEND_API_KEY); WhatsApp alerts via Twilio (needs user credentials)
- P1: Client uploads real project photos via dashboard (replace placeholder stock)
- P1: More project listings per category from arelectroprojects.com catalogue
- P2: SEO meta + sitemap; deployment readiness

## Next Tasks
1. Get Resend key / Twilio credentials from user to finish alerts
2. Client seeds real photos + full catalogue
