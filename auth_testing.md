# Auth Testing Playbook

Credentials live in /app/memory/test_credentials.md.

## MongoDB verification
```
mongosh
use test_database
db.users.find({role: "admin"}).pretty()
```
Verify: bcrypt hash starts with `$2b$`; unique index on users.email; index on login_attempts.identifier.

## API testing
```
curl -c cookies.txt -X POST http://localhost:8001/api/auth/login -H "Content-Type: application/json" -d '{"email":"arelectroprojects@gmail.com","password":"ARElectro@2026"}'
cat cookies.txt
curl -b cookies.txt http://localhost:8001/api/auth/me
```
Login returns the user object and sets `access_token` + `refresh_token` httpOnly cookies. `/me` returns the same user via cookies.

Admin-only routes (expect 401 without cookie): POST /api/admin/upload, POST /api/admin/projects, DELETE /api/admin/projects/{id}, PUT /api/admin/categories/{slug}, POST /api/admin/videos, DELETE /api/admin/videos/{id}, GET /api/inquiries.
