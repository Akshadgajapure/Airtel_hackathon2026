# Project Udyam Digital — Data privacy & security note

**Prototype scope.** This design uses synthetic hackathon data and mocked GSTIN/Udyam registries. It demonstrates privacy-by-design controls; it is not a legal opinion or a production DPDP compliance certification.

## Consent, purpose and minimisation
Before the first KYC upload, the owner sees a purpose-specific notice and must actively consent. The notice identifies the data collected (GSTIN/Udyam identifiers, registration documents, signatory ID and current address proof), the purposes (business identity verification, product eligibility and installation onboarding), the retention window, withdrawal/deletion route and grievance contact. Upload endpoints reject requests without consent. Each step requests only the document needed for that check. The advisor does not ask for KYC documents during needs discovery. Consent acceptance is timestamped with a purpose and audit ID; consent is not bundled with marketing consent.

## Verification and masking
GSTIN and Udyam lookups are mocked against local synthetic CSV registries. GSTIN validation checks 15-character structure and checksum and accepts `X` in the PAN entity-type position as required by this exercise. Cancelled/suspended registrations are blocked from activation and routed to a clear remediation path. OCR is a first-pass extraction aid, not proof of identity. Fuzzy OCR reconciliation is flagged for human review. Cross-document name consistency, registry status, signatory expiry/authority and address-proof freshness (0–90 days as of 15 July 2026) are checked. Identifiers are masked in UI summaries and logs; raw IDs should be encrypted and accessible only to authorised KYC roles in production.

## Security controls for production
- TLS 1.2+ in transit; managed envelope encryption / AES-256 at rest for document objects and database fields containing identifiers.
- Role-based least-privilege access, MFA for staff, short-lived signed upload URLs, malware scanning, file type/size limits and isolated OCR workers.
- No raw PII, document image or full identifier in LLM prompts, analytics events, application logs or support transcripts. Use redacted references and approved private inference only if an LLM is introduced.
- Append-only audit events for consent, lookup, upload, OCR result, reviewer decision, e-sign and deletion; alert on unusual access/export.
- Retain KYC document images for 180 days after onboarding for this prototype's declared schedule, then securely delete unless a specific legal obligation requires longer retention. Keep minimal audit metadata for a separately approved period. Production retention must be aligned to applicable telecom, tax, KYC and other sector-specific obligations before launch.
- Withdrawal is available through the grievance contact. Stop optional processing, revoke access, and delete data not required to be retained by law; explain any legally required retention to the requester. Provide a correction route for inaccurate OCR/registry matches.

## DPDP Act, 2023 operating posture
The product should provide clear notice, valid consent where consent is the chosen lawful basis, purpose limitation, data minimisation, reasonable security safeguards, grievance handling, correction/erasure workflows and breach response aligned with the DPDP Act, 2023 and rules/commencement requirements applicable at deployment. A Data Protection Officer or designated grievance contact should be named where legally required. Processor contracts, data-flow inventory, retention schedule and cross-border transfer assessment must be completed before production. The prototype stores uploaded images locally and runs OCR with local Tesseract. By default, the advisor uses a deterministic fallback. If an operator configures `OPENAI_API_KEY`, `OPENAI_BASE_URL` and `OPENAI_MODEL`, the optional explanation adapter sends only coarse business context (business type/segment, employee and site counts, city tier, language, pain point and eligible product names); it does not send identifiers, contact details, exact address or document contents. This is still a third-party processing path and must be disabled or assessed for processor terms, region, retention and cross-border transfer before any real-data use.

## Breach response
Maintain an incident playbook: contain access, preserve evidence, assess scope and affected data principals, notify the competent authority and affected individuals within legally prescribed timelines, remediate root cause, and document closure. Conduct periodic access reviews, vulnerability testing, backup/restore tests and vendor assessments.

**Grievance contact shown in prototype:** privacy@accel.example (fictional placeholder; replace with a monitored, approved address before any external pilot).
