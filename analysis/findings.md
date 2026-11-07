# Project Udyam Digital — Data findings

**Dataset:** 5,000 synthetic leads, Apr–Jun 2026. **Outcome:** 368 activations (7.36%).

## Funnel (cumulative stage reach)

| Stage | Leads | Stage-to-stage conversion |
|---|---:|---:|
| Lead | 5,000 | — |
| Contacted | 3,406 | 68.1% |
| Needs assessed | 1,974 | 58.0% |
| Quote accepted | 861 | 43.6% |
| KYC complete | 588 | 68.3% |
| Activated | 368 | 62.6% |

## Overall operating baseline

- Total acquisition spend: ₹5,539,640; CAC per activation: ₹15,053 (total cohort acquisition cost / 368 activations).
- Activated-customer average lead-to-activation time: 17.6 days; average status chases: 3.0.
- Six-month churn among activated customers: 15.2%; mean NPS score: 6.86.

## Segment economics

CAC = **total acquisition cost for every lead in segment / activated customers**, not cost only among winners. Payback shown as CAC divided by median monthly billings; it is a revenue proxy, not contribution-margin payback because gross margin is not supplied.

| Segment | Leads | Activation | CAC / activation | Median monthly value | Gross-billing payback | 6m churn | NPS |
|---|---:|---:|---:|---:|---:|---:|---:|
| Micro retail & services | 2,709 | 4.1% | ₹20,007 | ₹2,470 | 8.1 mo | 22.7% | 7.05 |
| Professional offices | 1,247 | 11.1% | ₹10,695 | ₹6,575 | 1.6 mo | 13.8% | 6.92 |
| Small manufacturers | 289 | 12.8% | ₹15,324 | ₹15,910 | 1.0 mo | 8.1% | 6.46 |
| Small multi-site businesses | 755 | 11.0% | ₹15,614 | ₹28,080 | 0.6 mo | 10.8% | 6.70 |

## Stage reach by segment, source, city tier, language and GSTIN

Counts are cumulative: a lead is counted at every stage whose timestamp is present. Full CSVs are saved as `funnel_by_*.csv`.

### Segment

| Group | Leads | Contacted | Needs assessed | Quote accepted | KYC complete | Activated | Activation rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| Small manufacturers | 289 | 191 | 129 | 83 | 69 | 37 | 12.8% |
| Professional offices | 1,247 | 864 | 538 | 285 | 212 | 138 | 11.1% |
| Small multi-site businesses | 755 | 498 | 299 | 168 | 133 | 83 | 11.0% |
| Micro retail & services | 2,709 | 1,853 | 1,008 | 325 | 174 | 110 | 4.1% |

### Lead source

| Group | Leads | Contacted | Needs assessed | Quote accepted | KYC complete | Activated | Activation rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| Referral | 413 | 326 | 230 | 111 | 79 | 61 | 14.8% |
| Inbound call | 504 | 404 | 224 | 100 | 78 | 48 | 9.5% |
| Channel partner | 1,010 | 719 | 408 | 196 | 128 | 81 | 8.0% |
| Field sales | 1,720 | 1,263 | 774 | 319 | 214 | 125 | 7.3% |
| Website form | 995 | 546 | 272 | 117 | 74 | 43 | 4.3% |
| WhatsApp campaign | 358 | 148 | 66 | 18 | 15 | 10 | 2.8% |

### City tier

| Group | Leads | Contacted | Needs assessed | Quote accepted | KYC complete | Activated | Activation rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1.0 | 2,578 | 1,751 | 1,019 | 451 | 304 | 221 | 8.6% |
| 2.0 | 2,422 | 1,655 | 955 | 410 | 284 | 147 | 6.1% |

### Preferred language

| Group | Leads | Contacted | Needs assessed | Quote accepted | KYC complete | Activated | Activation rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| Bengali | 111 | 76 | 46 | 22 | 16 | 10 | 9.0% |
| Malayalam | 83 | 61 | 33 | 19 | 10 | 7 | 8.4% |
| English | 1,168 | 803 | 481 | 213 | 151 | 94 | 8.0% |
| Hindi | 2,137 | 1,443 | 847 | 390 | 266 | 169 | 7.9% |
| Telugu | 207 | 134 | 74 | 32 | 24 | 16 | 7.7% |
| Marathi | 505 | 342 | 192 | 65 | 48 | 32 | 6.3% |
| Gujarati | 233 | 159 | 81 | 38 | 25 | 14 | 6.0% |
| Kannada | 253 | 185 | 97 | 38 | 25 | 13 | 5.1% |
| Tamil | 207 | 139 | 84 | 32 | 17 | 9 | 4.3% |
| Punjabi | 96 | 64 | 39 | 12 | 6 | 4 | 4.2% |

### Has GSTIN

| Group | Leads | Contacted | Needs assessed | Quote accepted | KYC complete | Activated | Activation rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| Y | 3,534 | 2,386 | 1,397 | 671 | 541 | 338 | 9.6% |
| N | 1,466 | 1,020 | 577 | 190 | 47 | 30 | 2.0% |

## Biggest drop reasons and product response

| Drop reason | Leads | Product / process response |
|---|---:|---|
| Unreachable after 3 attempts | 805 | Self-serve advisor + WhatsApp resume link |
| Owner had no time for a visit | 531 | Asynchronous mobile-first onboarding |
| Not interested on first call | 470 | Need-led discovery; suppress irrelevant pitch |
| Price too high | 414 | Good/better/best bundles; transparent total and spend comparison |
| Locked in with current provider | 325 | Switching-cost assessment; migration / backup proposition |
| Wrong or invalid number | 319 | Contact validation and channel preference |
| Visit not scheduled by sales | 296 | Self-serve quote and partner-assisted appointment |
| Only wanted a mobile plan | 280 | Right-size entry offer; avoid forcing broadband |
| Competitor offered cheaper plan | 207 | Comparable feature / SLA quote, not blanket discount |
| Quote too complex to understand | 206 | Plain-language line-item quote |
| Quote took too long to arrive | 179 | Instant rules-priced quote |
| Decided to wait | 107 | Targeted reason-code workflow / human escalation |
| Installation delayed beyond 21 days | 98 | Install-day-aware promise + tracker |
| Missing GST or Udyam document | 94 | Registry lookup + OCR pre-validation |
| Found paperwork too long | 79 | Consent-led progressive KYC |
| Customer cancelled before install | 53 | Proactive install-slot confirmation and cancellation save desk |
| Authorised signatory not available | 53 | Remote e-sign / delegated authority workflow |
| Document details did not match | 47 | Cross-document fuzzy match + manual review |
| Site not feasible for fibre | 41 | AirFiber alternative / feasibility check |
| First payment failed | 28 | UPI / card retry, payment link and clear failure recovery |

## Lead source economics

| Source | Leads | Activations | Conversion | CAC / activation | Decision |
|---|---:|---:|---:|---:|---|
| Referral | 413 | 61 | 14.8% | ₹4,099 | Scale |
| Inbound call | 504 | 48 | 9.5% | ₹5,113 | Scale |
| Channel partner | 1,010 | 81 | 8.0% | ₹20,851 | Optimise attribution & targeting |
| Field sales | 1,720 | 125 | 7.3% | ₹24,335 | Optimise attribution & targeting |
| Website form | 995 | 43 | 4.3% | ₹6,352 | Optimise attribution & targeting |
| WhatsApp campaign | 358 | 10 | 2.8% | ₹4,026 | Fix / controlled test |

## Propensity model

- Logistic regression with class weighting; stratified 75/25 split, random_state=42. Test ROC-AUC: **0.660**.
- Features are strictly lead-creation attributes: source, business profile, city tier/state/language, employee/site counts, turnover band, GST/Udyam availability, current connectivity/provider and spend. Excluded: stage dates, stage reached, drop reason, outcome, bundle, activation time, churn, NPS, CAC.
- Top decile lift table is in `propensity_top_decile_lift.csv`; coefficients in `propensity_drivers.csv`. Model is prioritisation support, not automated credit/eligibility.

| Score decile (1=highest) | Leads | Activations | Rate | Lift vs test average |
|---:|---:|---:|---:|---:|
| 1 | 125 | 21 | 16.8% | 2.28x |
| 2 | 125 | 13 | 10.4% | 1.41x |
| 3 | 125 | 11 | 8.8% | 1.20x |
| 4 | 125 | 11 | 8.8% | 1.20x |
| 5 | 125 | 7 | 5.6% | 0.76x |
| 6 | 125 | 7 | 5.6% | 0.76x |
| 7 | 125 | 10 | 8.0% | 1.09x |
| 8 | 125 | 7 | 5.6% | 0.76x |
| 9 | 125 | 3 | 2.4% | 0.33x |
| 10 | 125 | 2 | 1.6% | 0.22x |

## Strategic recommendation

1. **Professional offices** are the best first self-serve wedge: material volume, high conversion/value and 6-month retention better than micro. Use guided bundles and assisted exception handling.
2. **Micro retail & services** need WhatsApp/partner-assisted low-ticket offers; high price sensitivity and lower monthly value make expensive field acquisition uneconomic.
3. **Small multi-site businesses and manufacturers** are high-value but low-volume/longer-install segments; route qualified leads to named field sellers and installation specialists rather than forcing pure self-serve.
4. Scale referral and inbound-call motions; redesign partner/field economics and targeting before scaling them. Website conversion needs stronger qualification; WhatsApp campaign needs a controlled experiment before scaling based on observed conversion.
5. Pilot target scenario: 12.0% activation, ≤10-day average activation, ≤₹9,250 CAC at unchanged cohort acquisition spend, ≤1 status chase and ≤12% six-month churn. Funnel arithmetic and assumptions are documented in `target_scenario.md`; targets are hypotheses, not measured impact.

## Limitations

- Synthetic one-quarter data; segment samples, especially manufacturing, are small.
- Payback uses monthly billings as a proxy because contribution margin and gross margin are absent.
- Historical churn/NPS only exist for activated leads; non-activated leads are excluded.
- Model AUC is a holdout estimate and should be recalibrated on a time-based split before production.