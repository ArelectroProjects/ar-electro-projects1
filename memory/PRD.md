# PRD — AR ELECTRO Projects Website

## Original Problem Statement
Website for "AR ELECTRO Projects" — a project-building company for students. Multi-page site with About Us (company profile), project categories with photos (Diploma, Degree, Drone, Electronics, Electrical, Embedded, Mechanical, Biomedical, IoT), and a contact form. Theme: black + #e51a4D. CTAs: "Explore Projects" and "Contact on WhatsApp". YouTube channel link (youtube.com/@arelectroprojects). GSTIN 24DRWPA8036A1ZX. Reference: arelectroprojects.com.

## User Personas
- Diploma/Degree engineering students looking for ready/guided final-year projects
- Innovators wanting drones, IoT, embedded builds
- Company owner receiving inquiries via form + WhatsApp

## Architecture
- Frontend: React + Tailwind + shadcn-style components, multi-page routing (Home, Categories, Category Detail, About, Contact)
- Backend: FastAPI (`server.py`), all routes under /api
- DB: MongoDB via MONGO_URL, collection `inquiries`
- Config: frontend/.env (REACT_APP_BACKEND_URL), backend/.env (MONGO_URL, DB_NAME)
- Design system: /app/design_guidelines.json

## Core Requirements (static)
- Black + #e51a4D brand theme
- Category grid with project photos
- About Us company profile page
- Contact form: name, email, phone, project requirement
- WhatsApp CTA (wa.me/919998525347 — single constant in App.js)
- YouTube channel links
- GSTIN displayed on About/Footer

## Implemented (as of 2026-08-11)
- Multi-page React app: Home hero, categories grid, per-category detail pages, About, Contact
- Contact form -> POST /api/inquiries -> MongoDB (GET /api/inquiries exists for retrieval)
- Curated category imagery (placeholder stock, user-approved)
- WhatsApp + YouTube + email CTAs wired site-wide
- Mobile nav, responsive layout, data-testids on interactive elements
- E2E testing passed 100% (/app/test_reports/iteration_1.json); re-verified POST /api/inquiries + page flows 2026-08-11

## Backlog
- P0: None
- P1: Admin dashboard to upload real project photos & manage categories (Phase 2)
- P1: Replace placeholder category images with real client project photos
- P2: Split monolithic App.js into src/pages/ modules
- P2: Inquiry notification (email/WhatsApp alert on new submission)
- P2: SEO meta + sitemap

## Next Tasks
1. Collect real project photos from client; build upload/admin flow
2. Add per-category project listings (titles, descriptions, price hints)
3. Deployment readiness check when going live

## Credentials
No auth in the app. See /app/memory/test_credentials.md (no credentials required).
