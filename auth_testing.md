# Auth Testing Playbook (InkForge)

Auth = JWT email/password (httpOnly cookies `access_token` 15 min + `refresh_token` 7 days, Bearer header fallback) + Emergent-managed Google login (backend exchanges `session_id` at POST /api/auth/google/session and issues the same JWT cookies).

## API
```
API=$(grep REACT_APP_BACKEND_URL /app/frontend/.env | cut -d= -f2)
curl -c c.txt -X POST $API/api/auth/login -H 'Content-Type: application/json' -d '{"email":"owner.jakarta@inkforge.test","password":"Tattoo123!"}'
curl -b c.txt $API/api/auth/me
curl -b c.txt -X POST $API/api/auth/refresh
curl -b c.txt -X POST $API/api/auth/logout   # bumps session_version -> old tokens are 401
```
- Wrong password -> 401 "Invalid email or password"; 5 failures per ip+email -> 429 for 15 min (don't burn the seeded accounts).
- bcrypt hashes start with `$2b$` in db.users.password_hash.

## Browser
Log in through /login UI (cookies are httpOnly, secure, SameSite=None).
Google login cannot be automated (real Google account needed) — only verify the button redirects to auth.emergentagent.com.
