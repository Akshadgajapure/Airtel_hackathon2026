# 3-minute demo script — Project Udyam Digital

**0:00–0:25 | Problem + one insight**
“Accel has 5,000 synthetic SMB leads and only 368 activations — 7.4%. The largest preventable leak is not product demand: 805 leads are unreachable after three attempts and 531 owners had no time for a visit. We replace the visit-first motion with a mobile-first journey.”

**0:25–1:00 | Hindi advisor**
“Let's onboard a Tier-2 kirana store in Nagpur, three employees, one site, no active GSTIN. The advisor asks a few questions. Notice the key design: the assistant explains, but a deterministic catalogue engine decides eligibility. It recommends a low-cost fibre + business calling bundle. GST-dependent products are explicitly shown as locked, not silently omitted.”

**1:00–1:25 | Live quote**
“Here is one monthly total, GST separated, and one-time setup. Toggle an add-on. The total updates immediately. A dependent product cannot be added without its required connectivity parent. Contract floors and install days come from the product catalogue.”

**1:25–2:00 | Smart KYC**
“Before upload, the owner must give explicit purpose-specific consent. We can look up GSTIN and Udyam against mock registries and run OCR. In the supplied specimen audit, K01 is blocked because GST status is Cancelled; K04 needs a clearer GST certificate; K05 is missing its Udyam certificate; K11 has an address proof 257 days old, beyond the 90-day limit. OCR-corrected identifiers go to manual review. K12 is the only auto-approve in this specimen batch.”

**2:00–2:25 | Tracker**
“After the mock OTP e-sign, the order gets a unique ID. The expected activation date is based on the slowest product in the bundle. We can advance milestones and show proactive WhatsApp/SMS messages, with the next action always visible.”

**2:25–2:45 | Back office**
“The priority queue ranks unactivated leads with a logistic-regression propensity score. Open a lead to inspect its business profile and activity, assign it to inside sales, a channel partner, field sales, installation or KYC, and save a work status. Changes persist in SQLite and the full filtered queue can be exported. The model uses lead-creation fields only — no stage dates, drop reason or outcome leakage.”

**2:45–3:00 | Business case**
“Our pilot target is 12% activation: 5,000 leads to approximately 599 activations by improving contact, needs assessment, quote acceptance, KYC and post-KYC activation to 72%, 62%, 49%, 75% and 73%. At unchanged acquisition spend, CAC falls mechanically from ₹15,053 to about ₹9,250. We target 10-day average activation and one or fewer status chases, then validate churn and conversion through a controlled pilot.”
