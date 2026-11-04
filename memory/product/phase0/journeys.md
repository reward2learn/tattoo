# Phase 0 Journeys — Integration Proof

All journeys are API-level (curl / backend scripts). No product UI in this phase.

- id: JRN-1
  steps: Send chat request with model "Claude Sonnet 5.5" and message "I want a small fine-line rose on my inner wrist".
  expected: 200; non-empty reply relevant to a tattoo; response names provider/model Claude Sonnet 5.5.

- id: JRN-2
  steps: Same request with model "GPT 5.5".
  expected: 200; non-empty relevant reply; response names GPT 5.5.

- id: JRN-3
  steps: Same request with model "Gemini 3.1 Pro".
  expected: 200; non-empty relevant reply; response names Gemini 3.1 Pro.

- id: JRN-4
  steps: Send chat request with model "made-up-model".
  expected: 400 with message "Unsupported model"; no provider call made.

- id: JRN-5
  steps: Generate image with engine "GPT Image 1", prompt "minimalist fine-line rose tattoo design, black ink on white".
  expected: 200; returns a storage key + backend URL; fetching the URL returns an image content-type; Mongo record holds the key only (no base64).

- id: JRN-6
  steps: Generate image with engine "GPT Image 1" and transparent background requested.
  expected: Returned file is PNG with an alpha channel; corner pixels have alpha = 0.

- id: JRN-7
  steps: Generate image with engine "Nano Banana", same rose prompt.
  expected: 200; stored and fetchable as in JRN-5.

- id: JRN-8
  steps: Send the image from JRN-5 to "Nano Banana" edit with instruction "convert to black-and-grey shading".
  expected: 200; a new storage key different from the original; fetched image differs from original.

- id: JRN-9
  steps: Generate image with engine "fal.ai", same rose prompt.
  expected: 200; stored and fetchable as in JRN-5.

- id: JRN-10
  steps: Generate with engine "Auto" (new image), then edit with engine "Auto".
  expected: First response reports engine GPT Image 1; second reports Nano Banana.

- id: JRN-11
  steps: Generate image with an empty prompt.
  expected: 422; no storage object created; no provider call.

- id: JRN-12
  steps: Fetch one stored image per engine and compare dimensions with provider output.
  expected: Dimensions identical (no downscale).

- id: JRN-13
  steps: Create a checkout for 1000 cents USD.
  expected: 200 with a checkout.stripe.com URL; a transaction record exists with status "initiated", amount 1000, currency "usd".

- id: JRN-14
  steps: POST to the payment webhook with a forged/invalid signature.
  expected: 400; no transaction status changes.

- id: JRN-15
  steps: Deliver the same valid webhook event (or simulated completed session for the same session id) twice.
  expected: Transaction moves to "paid" once; a second delivery changes nothing; only one processed-event record exists.

- id: JRN-16
  steps: Request a new Stripe Connect Express account.
  expected: 200 with an account id starting "acct_". If Connect is not enabled, the response contains Stripe's error message verbatim (orchestrator escalates to user).

- id: JRN-17
  steps: Request an onboarding link for the JRN-16 account.
  expected: 200 with a connect.stripe.com URL.

- id: JRN-18 (human)
  steps: Human opens the onboarding link and completes it with Stripe test data; then request account status, then request a 100-cent transfer to it.
  expected: Status shows charges_enabled and payouts_enabled true; transfer returns an id starting "tr_".

- id: JRN-19
  steps: Request a test email to a given address.
  expected: 200 with a provider message id.

- id: JRN-20
  steps: GET /api/openapi.json.
  expected: 200 JSON listing the Phase 0 endpoints.
