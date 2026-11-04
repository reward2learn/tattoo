# InkForge PRD — Living Document

## Original problem statement
Multi-tenant Tattoo AI Design Platform (FARM) with marketplace and artist royalties. Product context: /app/memory/product/overview.md.
Phase 0 = integration POC: prove with real calls every risky dependency (3 chat LLMs, 3 image engines + Auto, object storage, Stripe Checkout + signed idempotent webhooks, Stripe Connect Express, managed email) as reusable backend services. No UI. Phase 0 spec: /app/memory/product/phase0/requirement.md, journeys.md.

## Architecture (backend/)
- core/: db.py (Motor + INDEXES), models.py (PyObjectId, BaseDocument), http.py (public_base_url)
- services/: llm_chat.py, image_engines.py, images.py, fal_media.py, storage.py, stripe_client.py, payments.py, connect.py, email.py, errors.py
- routes/: poc_ai.py, poc_payments.py, poc_email.py (thin)
- OpenAPI at /api/openapi.json, docs /api/docs

## Model mapping
- Claude Sonnet 5.5 → anthropic/claude-sonnet-5-5; GPT 5.5 → openai/gpt-5.5; Gemini 3.1 Pro → gemini/gemini-3.1-pro-preview
- GPT Image 1 → gpt-image-1.5 (env GPT_IMAGE_MODEL_ID; the proxy rejects gpt-image-1 with "model does not exist")
- Nano Banana → gemini-3.1-flash-image-preview; fal.ai → fal-ai/flux-2; Auto = GPT Image 1 for new images, Nano Banana for edits

## Implemented (2026-11, Phase 0)
- JRN-1..15, 19, 20 pass (21/21 backend tests, iteration_1). Provider errors → 424 with provider named.
- Stripe: claimable sandbox keys (STRIPE_SECRET_KEY/WEBHOOK_SECRET); tax mode: Stripe-managed (managed payments)
- JRN-16/17/18 BLOCKED: Connect not enabled on the sandbox (Stripe error is returned verbatim). Pod key sk_test_emergent → proxy returns 404 for all Connect endpoints.

## Backlog
- P0: claim the Stripe sandbox, enable Connect, re-run JRN-16..18
- P0: decide GPT Image 1 backing model (gpt-image-1.5 vs. none)
- Phase 1: auth (JWT + Google), roles, tenants, Redux store, shell, studios, seed data
- Hardening carry-over: cross-check webhook amount/currency against the stored txn; lifespan handler
