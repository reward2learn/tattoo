# Phase 1 Journeys — Foundation & Studios

Phase 0 journeys JRN-1..JRN-20 remain valid (API level).

## Accounts
- id: JRN-21
  steps: On the home page click Sign up, enter name, a new email, password "Tattoo123!", choose "I want a tattoo", submit.
  expected: User is signed in and lands on the client home; nav shows the user's name and "Sign out"; no studio or admin links.

- id: JRN-22
  steps: Sign up again with the same email.
  expected: "An account with this email already exists"; no second account created.

- id: JRN-23
  steps: Sign up with password "short".
  expected: "Password must be at least 8 characters"; account not created.

- id: JRN-24
  steps: Sign in with a seeded login but a wrong password.
  expected: "Invalid email or password"; still signed out.

- id: JRN-25
  steps: Sign in as the seeded client, reload the page 3 times.
  expected: Still signed in each time (Q-14).

- id: JRN-26
  steps: Click "Sign out", then press browser Back to the previous protected page.
  expected: Redirected to sign-in; protected content not shown.

- id: JRN-27
  steps: Open the sign-in page.
  expected: A "Continue with Google" button is visible and starts the Emergent Google login when clicked.

- id: JRN-28 (human)
  steps: Continue with Google using a Google account never used before; choose "I'm a tattoo artist".
  expected: Lands on artist home with "Independent" workspace.

- id: JRN-29
  steps: Signed out, open the studio dashboard URL directly.
  expected: Redirected to sign-in; after signing in as that studio's owner, returned to the dashboard.

## Roles & isolation
- id: JRN-30
  steps: Signed in as the seeded client, open the studio dashboard URL and the platform admin URL.
  expected: "You don't have access to this page" on both.

- id: JRN-31
  steps: As studio 1 owner (API), read and update studio 2's settings, list studio 2's team, invite to studio 2.
  expected: Every call returns 403; studio 2 data unchanged (Q-8).

- id: JRN-32
  steps: As studio 1 owner, call studio 1's update endpoint but include studio 2's id as tenantId in the body/query.
  expected: Only studio 1 changes (or request rejected); studio 2 unchanged.

- id: JRN-33
  steps: Call every protected endpoint with no token, then with a tampered token.
  expected: All return 401 (Q-9).

- id: JRN-34
  steps: As a studio 1 artist (API), try to update studio 1 branding or invite someone.
  expected: 403 (artists cannot manage studio settings or team).

## Studio creation & branding
- id: JRN-35
  steps: Sign up choosing "I run a studio".
  expected: Lands on "Create your studio"; typing name "Rumah Tinta Jakarta" auto-suggests slug "rumah-tinta-jakarta".

- id: JRN-36
  steps: In Create your studio, try slugs "ab", "Bad Slug!", the seeded studio 1 slug, and "admin".
  expected: Respectively "Use 3–40 lowercase letters, numbers or hyphens" (twice), "This studio URL is taken", "This studio URL is reserved".

- id: JRN-37
  steps: Create the studio with a valid slug, upload a PNG logo, set primary "#0F0F0F" and accent "#C8A96A", tagline, about, city, contact email, Instagram; save; open /t/<slug>.
  expected: Public page shows the logo (not stretched), name, tagline, about, city; brand colors visible; whole flow ≤ 5 minutes (Q-10, Q-13).

- id: JRN-38
  steps: Upload a .gif or .pdf as logo; then a PNG larger than 5 MB.
  expected: "Logo must be PNG, JPG or WebP"; then "Logo must be 5 MB or smaller"; previous logo unchanged.

- id: JRN-39
  steps: Enter color "red" or "#12" and save.
  expected: "Enter a valid hex color like #1A1A1A"; not saved.

- id: JRN-40
  steps: Signed out, open the seeded studio 1 page /t/<slug> and /t/<slug>/contact.
  expected: Page loads without sign-in showing logo, name, tagline, about, city and both active artists; contact page shows email, Instagram, city.

- id: JRN-41
  steps: Open /t/this-studio-does-not-exist.
  expected: "Studio not found".

## Team
- id: JRN-42
  steps: As studio 1 owner, open Team, invite a brand-new email as artist.
  expected: Invitation appears in the pending list; toast confirms; if email sending fails the toast reads "Invite created — email could not be sent" and the invite still exists.

- id: JRN-43
  steps: Sign up with that invited email choosing "I'm a tattoo artist".
  expected: Pending invitation from studio 1 shown after sign-up; Accept makes them an active artist; they appear on studio 1's team list and public roster.

- id: JRN-44
  steps: As the studio 1 owner, invite the email of an already-active studio 1 artist.
  expected: "Already a member of this studio"; no duplicate.

- id: JRN-45
  steps: Invite the seeded studio 2 artist to studio 1; sign in as that artist; Decline.
  expected: Invitation disappears; artist remains only in studio 2.

- id: JRN-46
  steps: Invite the seeded studio 2 artist to studio 1 again; they Accept; open workspace switcher.
  expected: Switcher lists "Independent", studio 1 and studio 2; switching changes the shown workspace name and persists while navigating.

- id: JRN-47
  steps: As studio 1 owner, remove an artist from the team.
  expected: Artist moves out of the active list (shown as former); disappears from the public roster; that artist can no longer call studio 1 artist APIs (403).

- id: JRN-48
  steps: As studio 1 sole owner, try to remove yourself.
  expected: "A studio needs at least one owner"; membership unchanged.

- id: JRN-49
  steps: Revoke a pending invitation.
  expected: Invitation removed; invited user no longer sees it.

- id: JRN-50
  steps: After JRN-42..JRN-49, inspect audit records via API/DB.
  expected: One audit record per invite, accept, decline, remove, revoke with actor, studio, target, time.

## Independent artist & shell
- id: JRN-51
  steps: Sign up choosing "I'm a tattoo artist" with no invitations.
  expected: Artist home shows "Independent" workspace; no studio dashboard link.

- id: JRN-52
  steps: Sign in as the seeded platform admin, open /platform/tenants.
  expected: Lists both seeded studios (plus any created) with name, slug, owner, active artist count, created date.

- id: JRN-53
  steps: At 375×812, visit /, sign-in, sign-up, /t/<studio1>, studio dashboard and team page.
  expected: No horizontal scroll; navigation collapses into a working mobile menu; nothing clipped (Q-12).

- id: JRN-54
  steps: Sign in as each role and look at the navigation.
  expected: Only links for that role's existing pages; no links to unbuilt areas (marketplace, chat, earnings).

- id: JRN-55
  steps: Open the home page signed out.
  expected: Landing page describes the platform with "Sign in" and "Sign up" actions.

## Redux (code/behaviour)
- id: JRN-56
  steps: Inspect frontend source.
  expected: `makeStore` with configureStore; ReduxProvider wraps the app; slices auth, tenant, chat, design, marketplace, royalty, notification, ui each under src/features/<name>/ with a selectors file; design slice matches the user's shape and actions; server data calls go through RTK Query (no ad-hoc axios/fetch in components).

- id: JRN-57
  steps: Sign in as studio 1 owner, view the dashboard, sign out, sign in as client.
  expected: No studio 1 data visible to the client anywhere (auth/tenant/RTK Query cache cleared on sign-out).

- id: JRN-58
  steps: GET /api/openapi.json.
  expected: Lists auth, studio, branding, team, invitation and admin tenant endpoints.
