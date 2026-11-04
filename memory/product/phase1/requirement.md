# Phase 1 — Foundation & Studios

Version: phase-1
Product context: `/app/memory/product/overview.md` (Stack, Personas & Roles, Business Decisions, UI/UX Rules). Phase 0 services (chat, images, storage, email) already exist under backend/services — reuse them.

## Goal
Anyone can create an account (email+password or Google), pick what they are (client, independent artist, studio owner), and studio owners can create a branded studio at `/t/:slug`, invite and remove artists. All of it runs on a Redux Toolkit + RTK Query client with central server-side authorization and strict tenant isolation. Demo users and 2 studios are seeded.

## Functional requirements

### Accounts & sign-in (F-2)
- REQ-31 [event] When a visitor submits sign-up with name, email, password and account type, the system shall create the account and sign them in.
- REQ-32 [always] The system shall offer exactly three sign-up account types: "I want a tattoo" (client), "I'm a tattoo artist" (independent artist), "I run a studio" (studio owner).
- REQ-33 [unwanted] If the sign-up email already exists, then the system shall show "An account with this email already exists".
- REQ-34 [unwanted] If the password is shorter than 8 characters, then the system shall show "Password must be at least 8 characters".
- REQ-35 [event] When a user signs in with correct email and password, the system shall issue a JWT session and land them on their role home.
- REQ-36 [unwanted] If sign-in credentials are wrong, then the system shall show "Invalid email or password".
- REQ-37 [event] When a user chooses "Continue with Google", the system shall sign them in through Emergent-managed Google login.
- REQ-38 [event] When a Google sign-in uses an email that already has an account, the system shall sign into that same account (interpreted).
- REQ-39 [event] When a first-time Google user signs in, the system shall ask them to choose an account type before continuing.
- REQ-40 [state] While a session is valid, the system shall keep the user signed in across page reloads.
- REQ-41 [event] When a user clicks "Sign out", the system shall end the session and return to the home page.
- REQ-42 [always] The system shall store passwords only as salted hashes.

### Roles & authorization (F-3)
- REQ-43 [always] The system shall support the roles client, artist, studio owner and platform admin.
- REQ-44 [always] The system shall store studio roles as memberships (user, studio, role owner|artist, status active|invited|former, joined_at, left_at).
- REQ-45 [always] The system shall allow one user to hold memberships in several studios.
- REQ-46 [always] The system shall enforce every protected API call through one central authorization policy module (authenticated → membership → role → resource ownership).
- REQ-47 [always] The system shall derive the active studio from the URL slug or the session membership, never from a tenantId supplied in a request body or query.
- REQ-48 [unwanted] If a user calls an API for a studio they are not an active member of, then the system shall respond 403.
- REQ-49 [unwanted] If a signed-in user opens an area their role cannot use, then the system shall show "You don't have access to this page".
- REQ-50 [unwanted] If a signed-out visitor opens a protected page, then the system shall redirect to sign-in and return them there after signing in.
- REQ-51 [always] The system shall create platform admins only through seeding or by another platform admin (no self sign-up).

### Redux Toolkit client state (F-4)
- REQ-52 [always] The system shall manage client state with Redux Toolkit through a single `makeStore` store and a ReduxProvider.
- REQ-53 [always] The system shall contain the slices auth, tenant, chat, design, marketplace, royalty, notification and ui, each with its selectors file, under `src/features/<name>/`.
- REQ-54 [always] The system shall fetch and cache all server data through RTK Query endpoints.
- REQ-55 [always] The system shall keep business records in the database, with Redux holding only session, UI and workflow state plus the RTK Query cache.
- REQ-56 [always] The system shall implement the design slice with the state shape and actions given in the user's plan (activeSessionId, selectedDesignId, generationStatus, generationProgress, error).
- REQ-57 [event] When the user signs out, the system shall clear the auth, tenant and RTK Query cache state.

### Studios (F-5)
- REQ-58 [event] When a studio owner submits a studio name and slug, the system shall create the studio with that owner as an active owner member.
- REQ-59 [always] The system shall suggest a slug from the studio name as lowercase letters, numbers and hyphens.
- REQ-60 [unwanted] If the slug is not 3–40 characters of lowercase letters, numbers and hyphens, then the system shall show "Use 3–40 lowercase letters, numbers or hyphens".
- REQ-61 [unwanted] If the slug is taken, then the system shall show "This studio URL is taken".
- REQ-62 [unwanted] If the slug is a reserved word (admin, api, auth, marketplace, dashboard, artist, platform, t, settings), then the system shall show "This studio URL is reserved".
- REQ-63 [event] When a studio owner without a studio signs in, the system shall send them to the "Create your studio" step.

### Branding & public studio page (F-6)
- REQ-64 [event] When an owner saves branding, the system shall store logo, primary color, accent color, tagline, about text, city, contact email and Instagram handle.
- REQ-65 [unwanted] If an uploaded logo is not PNG, JPG or WebP, then the system shall show "Logo must be PNG, JPG or WebP".
- REQ-66 [unwanted] If an uploaded logo exceeds 5 MB, then the system shall show "Logo must be 5 MB or smaller".
- REQ-67 [always] The system shall store logos in Emergent Object Storage.
- REQ-68 [unwanted] If a color is not a valid hex value, then the system shall show "Enter a valid hex color like #1A1A1A".
- REQ-69 [event] When anyone opens `/t/:slug`, the system shall show the studio's logo, name, tagline, about text, city and active artist roster without requiring sign-in.
- REQ-70 [state] While on any `/t/:slug/*` page, the system shall apply the studio's primary and accent colors.
- REQ-71 [event] When anyone opens `/t/:slug/contact`, the system shall show the studio's contact email, Instagram and city.
- REQ-72 [unwanted] If `/t/:slug` matches no studio, then the system shall show "Studio not found".

### Team management (F-7)
- REQ-73 [event] When an owner invites an email as artist, the system shall create an "invited" membership visible to that email's account.
- REQ-74 [event] When an invitation is created, the system shall send an invitation email through the managed email integration.
- REQ-75 [unwanted] If the invitation email fails to send, then the system shall keep the invitation and show "Invite created — email could not be sent" (interpreted).
- REQ-76 [unwanted] If the invited email is already an active member, then the system shall show "Already a member of this studio".
- REQ-77 [event] When someone signs up with an email that has pending invitations, the system shall show those invitations after sign-up.
- REQ-78 [event] When an artist accepts an invitation, the system shall set the membership to active.
- REQ-79 [event] When an artist declines an invitation, the system shall remove the pending invitation.
- REQ-80 [event] When an owner removes an artist, the system shall set that membership to "former" with a left_at timestamp.
- REQ-81 [unwanted] If the only owner tries to remove themselves, then the system shall show "A studio needs at least one owner".
- REQ-82 [event] When an owner revokes a pending invitation, the system shall delete it.
- REQ-83 [always] The system shall write an audit record for every membership change (invite, accept, decline, remove, revoke) with actor, studio, target and time.

### Independent artists (F-8)
- REQ-84 [event] When an independent artist signs up, the system shall give them an artist home with an "Independent" workspace.
- REQ-85 [state] While an artist has more than one workspace, the system shall show a workspace switcher listing "Independent" plus each active studio.
- REQ-86 [event] When an artist switches workspace, the system shall store the selection in Redux session state.

### App shell (F-9)
- REQ-87 [always] The system shall show navigation matching the user's roles: client home, artist home, studio dashboard, platform admin.
- REQ-88 [always] The system shall show navigation links only for pages that exist in the current build.
- REQ-89 [state] While the viewport is under 768 px wide, the system shall collapse navigation into a mobile menu.
- REQ-90 [event] When an action succeeds or fails, the system shall show a toast driven by the notification slice.
- REQ-91 [event] When a platform admin opens `/platform/tenants`, the system shall list every studio with name, slug, owner, active artist count and created date (interpreted).
- REQ-92 [always] The system shall show a public landing page at `/` describing the platform with sign-in and sign-up actions.

### Seed data
- REQ-93 [always] The system shall seed 1 platform admin, 2 studios each with an owner, 3 artists (2 active in studio 1, 1 active in studio 2) and 1 client, and write all logins to `/app/memory/test_credentials.md`.
- REQ-94 [always] The system shall seed the studios as Indonesian studios with logos, colors and complete branding (interpreted).

### Platform
- REQ-95 [always] The system shall keep `/api/openapi.json` current with every endpoint.

## Quality requirements
```
Q-8   Tag: Security.TenantIsolation  (breaks: exposure)
      Scale: cross-studio reads or writes that succeed
      Meter: API tests — owner/artist of studio 1 attempts read+write on studio 2 settings, team, invitations; plus tenantId injected in body/query (≥10 attempts)
      Must: 0
      Plan: 0
```
```
Q-9   Tag: Security.Auth  (breaks: lockout/exposure)
      Scale: protected endpoints reachable without a valid token
      Meter: call every protected endpoint with no token and with a tampered token
      Must: 0
      Plan: 0
```
```
Q-10  Tag: Usability.StudioSetup
      Scale: minutes for a first-time owner from sign-up to a live branded /t/:slug page
      Meter: tester walk-through, 1 run; human
      Must: ≤ 5 (estimate)
      Plan: ≤ 2 (estimate)
```
```
Q-11  Tag: Performance.PageLoad
      Scale: ms from navigation to studio page content visible
      Meter: browser timing, 3 loads of /t/:slug
      Must: < 3000
      Plan: < 1200
```
```
Q-12  Tag: Device.Responsive  (breaks: it broke on my device)
      Scale: pages with horizontal scroll or overlapping/clipped nav at 375 px width
      Meter: browser at 375×812 on /, sign-in, sign-up, /t/:slug, dashboard, team
      Must: 0
      Plan: 0
```
```
Q-13  Tag: Cosmetic.Logo
      Scale: logos rendered stretched, cropped or pixelated
      Meter: visual check of seeded + uploaded logo (square and wide) on /t/:slug and dashboard
      Must: 0
      Plan: 0
```
```
Q-14  Tag: Reliability.Session  (breaks: lockout)
      Scale: forced sign-outs on reload while token valid
      Meter: reload 5× on dashboard and artist home
      Must: 0
      Plan: 0
```
