# Requirements: InkForge — Tattoo AI Design Platform (working name)

## Core Value
Clients turn an idea into tattoo concepts through an AI consultation and send them to a studio; artists publish original/AI-assisted designs to a multi-tenant marketplace and earn tracked, immutable royalties every time a design is purchased or licensed.

## Stack (confirmed deviation from user's original Next.js/Prisma/Postgres plan)
- Frontend: React (CRA, React Router) + **Redux Toolkit + RTK Query** (mandatory) + Tailwind/shadcn.
- Backend: FastAPI. Database: MongoDB. Files: Emergent Object Storage (never base64 in Mongo).
- Redux = single source of truth for CLIENT state only (ui, session, workflow, cached server data via RTK Query). Database/API = authoritative source for all persistent business data. Nothing business-critical lives only in Redux.
- Required Redux structure (adapted to CRA `src/`): `src/app/store.js|ts` (makeStore), `src/providers/ReduxProvider`, `src/features/{auth,tenant,chat,design,marketplace,royalty,notification,ui}/` each with slice + selectors (+ `*Api` RTK Query endpoints where listed in user's plan: chat, design, marketplace, royalty).
- Money stored as integer minor units (cents) + currency code. USD only for MVP.
- Prisma schema from the user's plan is the reference data model; translate to Mongo collections with equivalent fields, enums, unique indexes (e.g. `idempotencyKey` unique, royalty `(sourceEventId, artistUserId, designId)` unique).

## Personas & Roles
| Role | Who | Key permissions |
|---|---|---|
| Client / Buyer | Person wanting a tattoo | AI consultation, concepts, browse/search marketplace, favorite, purchase/license, download licensed files, request consultation, report |
| Artist | Tattoo artist — member of a studio OR independent | Artist Studio workspace, upload/generate designs, metadata, pricing, versions, submit for review, publish/unpublish (after approval), usage analytics, earnings, payout onboarding |
| Studio Owner (Tenant owner) | Owner/manager of a tattoo business (tenant) | Studio branding/settings, team (invite/remove artists), approve artist designs, feature listings, assign designs, marketplace visibility & settings, consultation inbox, revenue view, studio payout onboarding |
| Platform Admin | Platform operator | All tenants, suspend tenants, moderation, reports, disputes, audit logs, royalty rules/commission, payout config, royalty adjustments, platform settings |

Rules: a user can belong to multiple tenants with a role per tenant. Tenant context is always derived from the authenticated session membership or the trusted URL slug — never trusted from a browser-supplied tenantId. Authorization is enforced centrally via policy functions (authenticated → tenant membership → role → resource ownership → marketplace visibility → license rights → allowed usage).

## Features
| id | Feature | Persona | Phase |
|---|---|---|---|
| F-1 | Proof that all risky integrations work: 3 chat models, 3 image engines, Stripe Checkout + signed webhooks, Stripe Connect Express onboarding/transfer, managed email | system | 0 |
| F-2 | Sign up / sign in with email+password (JWT) AND Emergent-managed Google login | all | 1 |
| F-3 | Roles (client, artist, studio owner, platform admin), tenant membership, central authorization policies | all | 1 |
| F-4 | Redux Toolkit store + RTK Query + ReduxProvider with the slice structure above (ui, session, workflow state categories) | engineering | 1 |
| F-5 | Self-serve studio (tenant) creation with unique slug; tenant slug routing `/t/:slug` | studio owner | 1 |
| F-6 | Studio branding (logo, colors) + studio public landing page | studio owner, client | 1 |
| F-7 | Team management: invite artists, assign roles, remove artist | studio owner | 1 |
| F-8 | Independent artist accounts (not tied to a studio) | artist | 1 |
| F-9 | App shell with responsive, role-aware navigation (dashboard, artist, platform, marketplace areas); toasts; mobile nav | all | 1 |
| F-10 | AI consultation chat with model dropdown: Claude Sonnet 5.5, GPT 5.5, Gemini 3.1 Pro (anyone can pick) | client | 2 |
| F-11 | Structured tattoo questionnaire in chat (idea, style, placement, size, color, references) + design brief extraction | client | 2 |
| F-12 | Conversation persistence + history | client | 2 |
| F-13 | Concept generation (several concepts per request) with image engine dropdown: Auto (GPT Image 1 for new, Nano Banana for edits), GPT Image 1, Gemini Nano Banana, fal.ai; generation queue/status/progress | client | 2 |
| F-14 | Concept gallery: review, favorite, regenerate, edit (AI edit), download | client | 2 |
| F-15 | Reference image upload in chat | client | 2 |
| F-16 | Send concept to studio / submit consultation request; studio consultation inbox; email notification to studio | client, studio owner | 2 |
| F-17 | Artist Studio workspace (separate from client chat) with workspace selector (studio vs independent) | artist | 3 |
| F-18 | Upload original artwork: type/size validation, image re-encode, private originals, public thumbnails, signed download URLs | artist | 3 |
| F-19 | Studio AI generator: blank prompt, variations, black-and-grey, color, stencil-oriented, placement mockups; engine dropdown; upload final edited artwork | artist | 3 |
| F-20 | Design metadata: title, description, tags, style, body placement, color type, approx size, difficulty, price, license, usage restrictions, AI-assisted disclosure, originality confirmation, reference files, artist notes | artist | 3 |
| F-21 | Ownership & provenance: creator, rights owner (studio by default), tenant, source type, AI provider, prompt/brief, references, artist-edited flag, royalty eligibility | system | 3 |
| F-22 | Drafts, design versioning (major content change → new version; history immutable), archive, file management | artist | 3 |
| F-23 | Listing lifecycle: Draft → Submitted → Approved → Published → Suspended/Unpublished → Archived; studio approval required unless tenant allows auto-publish | artist, studio owner | 4 |
| F-24 | Tenant marketplace settings (all MarketplaceSettings fields) + modes: private, tenant-public, global, hybrid (per-design visibility) | studio owner | 4 |
| F-25 | Marketplace pages `/marketplace`, `/marketplace/:id`, `/t/:slug/marketplace`, `/t/:slug/marketplace/:id`; search + filters (style, placement, color, price, artist, tenant, trending, newest, most used, most favorited, AI vs artist-uploaded) | client | 4 |
| F-26 | Design detail page: full preview, artist, studio, description, style, placement, size, license terms, price, usage count, actions (Use this design, Request consultation, Purchase/license, Report) | client | 4 |
| F-27 | Favorites, featured listings, counts (views, favorites, usage, sales) | client, studio owner | 4 |
| F-28 | Idempotent usage events (viewed, favorited, downloaded, purchased, licensed, attached_to_consultation, used_in_booking, used_in_completed_tattoo, remixed, reported) + artist usage analytics | system, artist | 4 |
| F-29 | "Use this design" → intent (personal inspiration / exact design / modifications / book with artist) → consultation; chatbot knows the source design; no license-violating derivatives | client | 4 |
| F-30 | Studio marketplace tools: approve/reject, feature, assign designs to artists, visibility per design, usage & revenue review | studio owner | 4 |
| F-31 | Artist departure: listings move to the artist's profile; studio keeps rights + commission; artist keeps royalties | studio owner, artist | 4 |
| F-32 | Report a design (8 reasons from user's list) | client | 4 |
| F-33 | Tattoo-use-only license; license records; "My licenses"; block duplicate license for same version | client | 5 |
| F-34 | Stripe Checkout purchase/license with price snapshot; signature-verified, idempotent payment webhooks | client | 5 |
| F-35 | Versioned royalty rules (event types sale/license/booking/usage; sale + license active), default Artist 70 / Studio 10 / Platform 20 (platform covers Stripe fees); overrides per tenant/design/artist | platform admin | 5 |
| F-36 | Immutable royalty ledger (earned, adjusted, refunded, paid, reversed); statuses pending/available/processing/paid/refunded/reversed/disputed; balances computed from ledger | system | 5 |
| F-37 | Artist earnings dashboard (sales, downloads, usage, royalty history, summary); studio revenue view | artist, studio owner | 5 |
| F-38 | Stripe Connect Express onboarding for artists and studios (identity, bank, tax handled by Stripe; no bank data stored) | artist, studio owner | 5 |
| F-39 | Payouts: min $25, monthly schedule, 7-day settlement hold (all configurable); manual payout review; failed payouts; payout webhooks | platform admin, artist | 5 |
| F-40 | Refunds & chargebacks → reversal ledger entries; already-paid royalties offset against future earnings; chargeback → disputed hold | system | 5 |
| F-41 | Licensed file downloads via signed, expiring URLs | client | 5 |
| F-42 | Platform admin dashboard: tenants, suspend tenant, usage monitoring | platform admin | 6 |
| F-43 | Moderation queue: review, approve, reject, request changes, suspend listing, remove infringing material | platform admin | 6 |
| F-44 | Reports review + disputes (Published → Under dispute → Suspended → Resolved; lock design; hold related royalties) | platform admin | 6 |
| F-45 | Audit log viewer (ownership, royalty rule, moderation, tenant changes — writes begin in the phase each change type ships) | platform admin | 6 |
| F-46 | Admin royalty ledger view + adjustments | platform admin | 6 |
| F-47 | Platform settings: commission rates, royalty rules, payout config, marketplace policies, AI defaults | platform admin | 6 |
| F-48 | Rate limits (image generation, auth, chat) | system | 7 |
| F-49 | File security hardening (MIME/size limits, re-encode; AV scanning is a declared deviation) | system | 7 |
| F-50 | Webhook reliability, DB indexes, scheduled jobs (royalty availability, payout runs) | system | 7 |
| F-51 | Privacy controls: user can export and delete their account data (interpreted) | all | 7 |
| F-52 | Accessibility + responsive review; automated tests for royalty math, commission rules, permissions, tenant isolation, license validation, idempotency, Redux reducers/selectors | system | 7 |

## Phases
(Re-ordered after Phase 0 at user's request: "implement Stripe and payment later, build the rest first". Payments/royalties phase moved to the end.)
- **Phase 0 — Integration proof (POC)** → DONE (tester iteration_1: 8/8 pass; Stripe Connect blocked — unclaimed SG sandbox, deferred) → F-1. Docs: [phase0/requirement.md](phase0/requirement.md), [phase0/journeys.md](phase0/journeys.md)
- **Phase 1 — Foundation & Studios** → auth, roles, tenants, Redux, shell, studio branding/team, seed users & studios → F-2..F-9. Docs: [phase1/requirement.md](phase1/requirement.md), [phase1/journeys.md](phase1/journeys.md)
- **Phase 2 — AI Tattoo Consultation** → client chat → concepts → gallery → send to studio → F-10..F-16
- **Phase 3 — Artist Studio** → artist workspace, uploads, AI tools, metadata, provenance, versions → F-17..F-22
- **Phase 4 — Marketplace** → lifecycle, approvals, settings/modes, browse/filter/detail, favorites, usage tracking, use-this-design, departure, reporting → F-23..F-32 (Purchase/license button not shown until Phase 7)
- **Phase 5 — Moderation & Platform Admin** → F-42..F-45, F-47 (marketplace policies + AI defaults only; commission/royalty/payout settings move to Phase 7)
- **Phase 6 — Hardening** → F-48..F-52 (payment webhook/payout jobs hardened in Phase 7)
- **Phase 7 — Licensing, Payments & Royalties (deferred)** → F-33..F-41, F-46, commission/royalty/payout settings of F-47. Provider decision pending: user is Indonesia-based; Stripe Indonesia is invite-only preview with no cross-border; Xendit xenPlatform (split payments + payouts) is the local alternative. Revisit with user before this phase.

## UI/UX Rules
- Premium, dark, editorial look fitting tattoo culture; artwork is the hero. Images always keep aspect ratio (object-contain on neutral backgrounds), never stretched, never upscaled blurry; thumbnails sharp.
- Fully responsive; mobile nav works on 375px width.
- Studio pages `/t/:slug/*` apply the studio's logo and brand colors.
- Every AI-assisted listing shows an "AI-assisted" badge; attribution (artist + studio) always visible on listings.
- Money always shown with currency symbol and 2 decimals ($70.00).
- Generation shows status (queued → generating → completed/failed) with progress; failures show a retry action, never a silent blank.
- Model and engine dropdowns are visible in chat and Artist Studio; default chat model Claude Sonnet 5.5, default image engine "Auto".
- Clients can browse marketplace and studio pages without signing in; sign-in required to chat/generate, favorite, purchase, report (interpreted — protects AI cost).

## Integrations
| Need | Choice | Key |
|---|---|---|
| Chat LLMs | Claude Sonnet 5.5, GPT 5.5, Gemini 3.1 Pro — user-selectable dropdown | Emergent Universal Key |
| Image generation/editing | OpenAI GPT Image 1 (runs on model gpt-image-1.5 — approved by user; gpt-image-1 unavailable on Universal Key) (new + transparent PNG), Gemini Nano Banana (edits/variations), fal.ai (Flux-family model) + "Auto" = GPT Image 1 for new / Nano Banana for edits — user-selectable | Emergent Universal Key (fal.ai via Universal Key) |
| Payments | Stripe Checkout (test mode) | Stripe test key from pod env — never ask user |
| Payouts | Stripe Connect Express (test mode), real onboarding; separate charges & transfers to artist + studio connected accounts | same Stripe test key (Connect availability proven in Phase 0) |
| Email | Emergent-managed Resend (studio notified on new consultation) | managed, no key |
| Auth | JWT email/password + Emergent-managed Google login | — |
| File storage | Emergent Object Storage; private originals, public thumbnails, signed URLs | env (configured) |

## Business Decisions (confirmed)
- Rights owner by default: the studio (tenant) the artist belongs to when the design is created. Independent artist → artist is rights owner. Creator (artist) always recorded separately.
- Artist departure: studio keeps rights + its commission; listings move to the artist's profile (attribution no longer shows the studio as the artist's current studio; listing stays live); artist keeps receiving the artist royalty.
- Royalty trigger (MVP): purchase and license only. Booking/completed-tattoo/usage events are tracked, rule engine supports them, but no active rule by default.
- Split default: Artist 70% / Studio 10% / Platform 20%; platform covers Stripe fees. Independent artist sale: studio share goes to platform unless admin rule says otherwise (interpreted). Rules versioned; changes never rewrite history.
- License (MVP): single type TATTOO_USE_ONLY; other enum values exist but disabled. Derivatives/remix licensing deferred.
- Payouts: min $25, monthly, 7-day hold — configurable by platform admin.
- Refunds: reverse pending royalty; if already paid, negative adjustment offsets future earnings. Chargeback → disputed (held).
- Studio onboarding: self-serve.
- Notifications: studio dashboard + email.
- allowClientGeneratedListings default false.

## Edge Cases
- Duplicate webhook / usage event → processed once (idempotency key `royalty:{event_type}:{source_id}:{design_id}:{artist_id}`).
- Buyer already holds license for same design version → "You already own this license"; purchase blocked.
- Price changes during checkout → charged price = snapshot at checkout start.
- Editing artwork of a published design → new version; previous buyers keep v1 rights and file.
- Disputed design → listing hidden; related pending royalties held.
- AI never uses a marketplace design image as a generation reference; "Request modifications" routes to the artist/studio instead of AI-generating a derivative.
- Tenant suspended → its storefront and listings hidden; existing licenses remain valid and downloadable.
- Artist removed from studio mid-review → pending submissions remain with studio for approval decision.
- Connected account not onboarded → royalties accrue as available, payout waits; artist sees "Finish payout setup".
- Generation failure / provider down → error shown with retry; no partial records left as "completed".

## Seed Data
- 1 platform admin, 2 studios (each with an owner), 3 artists (2 in studio A, 1 in studio B), 1 client. Credentials in `/app/memory/test_credentials.md`.
- ~12 designs across the 3 artists (seeded when Phase 3/4 lands): mostly published, plus 1 draft and 1 pending review to demo approval; mix of AI-assisted and uploaded; varied styles/placements/prices.

## Declared Deviations
- Next.js/Prisma/Postgres → React/FastAPI/MongoDB (confirmed).
- No antivirus scanning available; mitigated by strict MIME/size checks + full image re-encode.
- Custom domains, backups, external error monitoring are hosting concerns, outside the app build.
