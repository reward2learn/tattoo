# Phase 0 — Integration Proof (POC)

Version: phase-0
Product context: see `/app/memory/product/overview.md` (Integrations table, Business Decisions).

## Goal
Prove, with real calls in this environment, that every risky external dependency works before any product UI is built on it: three chat models, three image engines (+ edit + transparent PNG), Emergent Object Storage, Stripe Checkout with signature-verified idempotent webhooks, Stripe Connect Express onboarding + transfer, and managed email. Output is backend services/endpoints that later phases reuse — no product UI required.

## Functional requirements

Chat
- REQ-1 [always] The system shall return a chat reply from Claude Sonnet 5.5 through the Emergent Universal Key.
- REQ-2 [always] The system shall return a chat reply from GPT 5.5 through the Emergent Universal Key.
- REQ-3 [always] The system shall return a chat reply from Gemini 3.1 Pro through the Emergent Universal Key.
- REQ-4 [unwanted] If a chat request names a model outside the three supported models, then the system shall respond 400 with "Unsupported model".
- REQ-5 [unwanted] If a chat provider call fails, then the system shall respond with an error naming the provider.

Images
- REQ-6 [event] When a text prompt is sent to GPT Image 1, the system shall return a generated tattoo image.
- REQ-7 [event] When a transparent background is requested from GPT Image 1, the system shall return a PNG whose background pixels are fully transparent.
- REQ-8 [event] When a text prompt is sent to Gemini Nano Banana, the system shall return a generated tattoo image.
- REQ-9 [event] When an edit instruction plus a stored image is sent to Gemini Nano Banana, the system shall return a new edited image.
- REQ-10 [event] When a text prompt is sent to fal.ai through the Emergent Universal Key, the system shall return a generated tattoo image.
- REQ-11 [event] When the "Auto" engine is requested for a new image, the system shall use GPT Image 1.
- REQ-12 [event] When the "Auto" engine is requested for an edit, the system shall use Gemini Nano Banana.
- REQ-13 [always] The system shall store every generated image in Emergent Object Storage and save only its storage key in MongoDB.
- REQ-14 [unwanted] If an image prompt is empty, then the system shall respond 422 without calling any provider.
- REQ-15 [unwanted] If an image engine call fails, then the system shall respond with an error naming the engine.
- REQ-16 [always] The system shall serve a stored image back through a backend route at its original resolution.

Payments
- REQ-17 [event] When a checkout is requested for an amount, the system shall create a Stripe Checkout session in test mode and return its URL.
- REQ-18 [event] When a checkout session is created, the system shall record a payment transaction with status "initiated".
- REQ-19 [event] When a valid Stripe payment webhook arrives, the system shall mark the matching transaction "paid".
- REQ-20 [unwanted] If a webhook signature is invalid, then the system shall respond 400.
- REQ-21 [unwanted] If the same webhook event arrives twice, then the system shall apply it once.

Payouts (Stripe Connect)
- REQ-22 [event] When a connected account is requested, the system shall create a Stripe Connect Express account in test mode.
- REQ-23 [event] When an onboarding link is requested for a connected account, the system shall return a Stripe-hosted onboarding URL.
- REQ-24 [event] When a connected account status is requested, the system shall return whether charges and payouts are enabled.
- REQ-25 [event] When a transfer is requested to an onboarded connected account, the system shall create a Stripe test transfer.
- REQ-26 [unwanted] If Stripe Connect is unavailable for the platform key, then the system shall return Stripe's error message verbatim.

Email
- REQ-27 [event] When a test email is requested, the system shall send it through the Emergent-managed email integration and return the provider message id.
- REQ-28 [unwanted] If email sending fails, then the system shall return the provider error.

Platform
- REQ-29 [always] The system shall expose the API contract at `/api/openapi.json`.
- REQ-30 [always] The system shall store money as integer cents plus a currency code.

## Quality requirements

```
Q-1  Tag: AI.ImageQuality
     Scale: generated images per engine that read as a clean tattoo design (clear linework, centered subject, plain background, no garbled text/watermark)
     Meter: human review of 3 prompts × each engine
     Must: 2 of 3 per engine
     Plan: 3 of 3 per engine
```
```
Q-2  Tag: AI.ChatLatency
     Scale: seconds from request to complete reply
     Meter: 3 timed calls per model
     Must: < 25 s (estimate)
     Plan: < 10 s (estimate)
```
```
Q-3  Tag: AI.ImageLatency
     Scale: seconds from request to stored image
     Meter: 3 timed calls per engine
     Must: < 120 s (estimate)
     Plan: < 45 s (estimate)
```
```
Q-4  Tag: Image.Fidelity
     Scale: stored image dimensions vs provider output dimensions
     Meter: compare dimensions of 1 image per engine
     Must: identical (no downscale, no re-crop)
     Plan: identical
```
```
Q-5  Tag: Payments.WebhookSecurity
     Scale: % of invalid-signature webhooks rejected
     Meter: curl with 3 forged signatures
     Must: 100%
     Plan: 100%
```
```
Q-6  Tag: Payments.Idempotency  (breaks: money)
     Scale: records changed per replayed webhook event
     Meter: replay same event 3×
     Must: exactly 1 state change total
     Plan: exactly 1
```
```
Q-7  Tag: Payouts.ConnectAvailability  (breaks: money)
     Scale: Connect account create + onboarding link success
     Meter: 1 API call each; transfer after human-completed test onboarding
     Must: account + link created; transfer succeeds after onboarding
     Plan: same
```
