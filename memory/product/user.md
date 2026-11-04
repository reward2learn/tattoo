# User Learning

## Profile (inferred)
- Arrived with a very detailed, technical product plan (Redux Toolkit, Prisma schema, API list, phased roadmap). Comfortable with architecture vocabulary; thinks in systems and edge cases.
- Prefers: hardened, short plan after questions; explicit approval gate before implementation ("implementation should remain paused until you approve").
- Language: English.

## Purpose
- App: Tattoo AI Design Platform (multi-tenant: studios + artists + clients + platform operator) with marketplace and artist royalties.
- Purpose: likely a platform business (SaaS/marketplace) — NOT yet confirmed. Unknown whether user is a tattoo artist/studio owner or a founder outside the industry.
- Users: tattoo clients (buyers), tattoo artists, studio owners (tenants), platform admin.

## Open questions to ask naturally
- Are they in the tattoo industry themselves (own studio / artist) or building the platform as a founder?
- Do they already have studios/artists lined up for launch?

## Location / market
- Business + most artists based in **Indonesia**. Matters for payments (Stripe ID is invite-only preview; Xendit xenPlatform likely better) and possibly IDR pricing / Bahasa Indonesia UI later.
- Wants payments built LAST ("build the rest first"). No tax handling for now. Approved gpt-image-1.5 as GPT Image 1 backing model.

## Decisions style (observed)
- Picks "all options" when offered providers (wants all 3 chat LLMs + all image engines, user-selectable dropdown) → values flexibility/choice over simplicity.
- Mostly accepts recommended defaults on business rules, but overrides on ownership (studio owns rights) → studio-centric business view; protects studio interests.
- Wants REAL Stripe Connect onboarding (not a mock) → wants production-realistic money flows.

## Suggestions made
- (none yet)
