# Pilot target scenario — funnel arithmetic

All baselines below are computed from the supplied synthetic Q2 cohort (5,000 leads, 368 activations). Targets are proposed pilot operating goals, not observed results or model predictions.

## Conversion bridge

| Funnel stage | Observed leads | Observed stage conversion | Pilot stage conversion assumption | Implied pilot volume |
|---|---:|---:|---:|---:|
| Leads generated | 5,000 | — | — | 5,000 |
| Contacted | 3,406 | 68.1% of leads | 72% of leads | 3,600 |
| Needs assessed | 1,974 | 58.0% of contacted | 62% of contacted | 2,232 |
| Quote accepted | 861 | 43.6% of needs assessed | 49% of needs assessed | 1,094 |
| KYC complete | 588 | 68.3% of quote accepted | 75% of quote accepted | 820 |
| Activated | 368 | 62.6% of KYC complete | 73% of KYC complete | 599 |

The arithmetic is sequential: 5,000 × 72% × 62% × 49% × 75% × 73% = approximately **599 activations**, or **12.0% lead-to-activation**, versus the observed 7.36%. This is a +231 activation improvement in a same-sized 5,000-lead cohort. The stage assumptions are pilot hypotheses to validate, not guaranteed outcomes.

## Operating targets and financial guardrails

| Metric | Observed baseline | Pilot target | Rationale / validation |
|---|---:|---:|---|
| Lead-to-activation | 7.36% | 12.0% | Funnel bridge above; instrument every stage and compare pilot/control cohorts. |
| Lead-to-activation time | 17.6 days average | ≤10 days average | Instant quote, progressive KYC, installation-day-aware promise and escalation SLA. This is an operating target, not implied by conversion arithmetic. |
| Blended CAC per activation | ₹15,053 | ≤₹9,250 | At 599 activations and unchanged ₹55.40 lakh cohort acquisition spend, implied CAC is ₹9,248. Cost reductions would improve this further; do not claim lower spend without evidence. |
| Status-chase calls | 3.0 average | ≤1.0 | Tracker, proactive milestone notifications and explicit next-action card. Validate using support/call logs. |
| 6-month churn | 15.2% | ≤12.0% | Retention hypothesis; requires a fully matured six-month pilot cohort and like-for-like segment mix. |

## Leak ownership

- Reachability / visit friction: 805 unreachable + 531 no time for visit + 296 visit not scheduled = 1,632 records potentially addressed by self-serve, asynchronous follow-up and partner appointment booking. Do not assume all are recoverable.
- Quote friction: 206 complex quote + 179 slow quote = 385 records addressed by deterministic instant pricing and plain-language quote.
- KYC friction: 94 missing GST/Udyam + 79 paperwork too long + 47 detail mismatch = 220 records addressed by registry prefill, OCR and explainable mismatch review.
- Installation friction: 98 delayed installation + 53 pre-install cancellation = 151 records addressed by capacity-aware promises, progress tracking and proactive save desk.

Categories above are observed drop reasons. A lead may still have other reasons not represented by the proposed intervention; pilot attribution is required before assigning causal lift.

## Segment and channel deployment

- Professional offices: first self-serve pilot wedge; 11.1% observed activation and ₹10,695 CAC per activation.
- Micro retail/services: low-ticket WhatsApp-first and partner-assisted; 4.1% activation and ₹20,007 CAC argue against expensive field-led acquisition.
- Multi-site and manufacturers: assisted selling and site survey; their higher monthly values justify specialist effort, but samples are smaller.
- Referral and inbound call: scale with source-level monitoring (14.8% / 9.5% activation; ₹4,099 / ₹5,113 CAC).
- WhatsApp campaign: do not scale unchanged (2.8% activation); run a controlled creative/qualification experiment first.

## Interpretation guardrails

- CAC is total acquisition cost across all leads in a source/segment divided by its activations.
- Payback in the analysis is CAC divided by median monthly billings. It is a revenue proxy because contribution margin is not provided.
- Churn/NPS are available only for activated customers. Segment-level retention comparisons are descriptive and subject to small samples.
- Propensity ROC-AUC 0.660 is a stratified random holdout result; use time-based validation before production use.
