# Operations dashboard guide

## What is live

The dashboard is not a static mock-up. It reads the 5,000-row synthetic lead file through FastAPI on each request and computes its summary from the underlying records. The propensity model is loaded from `analysis/propensity_model.joblib` and scores the non-activated leads using only attributes available at lead creation.

## Dashboard areas

- **KPI strip:** total leads, activations, observed lead-to-activation conversion, blended acquisition cost per activation, average activation time, six-month churn among activated customers, and average status-chase calls.
- **Acquisition funnel:** cumulative number of leads reaching each stage.
- **Segment and source charts:** observed activation conversion with lead/activation counts and CAC per activation. Click a segment or source row to filter the callback queue.
- **Drop reasons:** highest-volume reasons among non-activated leads.
- **Priority callback queue:** search by lead ID, business name, city or drop reason; filter by segment, lead source, city tier, funnel stage and minimum propensity score; sort by propensity, recency or acquisition cost; paginate through results.
- **Lead profile drill-down:** click a business name to open the profile, funnel stage, drop reason, lead-creation attributes, masked contact and propensity score. The detail endpoint omits raw GSTIN/Udyam identifiers and full contact names.
- **Assignment workflow:** choose an owner team and work status, then press Save. The API validates the lead, team and status. Current assignment and append-only assignment events are stored in local SQLite (`runtime_ops.db`) and remain after an app restart on the same machine.
- **CSV export:** downloads every record matching the current filters, including model scores and assignment metadata (not just the currently visible page).

## Metric definitions

- **Lead-to-activation:** activated leads / all leads in the supplied cohort.
- **Blended CAC per activation:** sum of acquisition cost across all leads / activated leads. This is not CAC per lead.
- **Average activation time:** mean `days_lead_to_activation` among activated leads.
- **Six-month churn:** share of activated leads with `churned_within_6_months == Y`.
- **Status chases:** mean `customer_follow_up_calls` among activated leads.
- **Segment/source CAC:** sum of acquisition costs for all leads in that segment/source / activations in that segment/source. It is null when there are no activations.
- **Funnel stage reach:** a lead is counted at a stage if its furthest recorded `stage_reached` is that stage or any later stage.

## Model governance

The current logistic-regression model has a stratified random holdout ROC-AUC of approximately 0.660. Features are lead-creation attributes only: source, business profile, location tier/state/language, employee/site counts, turnover band, GST/Udyam availability, current connectivity/provider and current spend. Stage dates, furthest stage, drop reason, outcome, selected bundle, activation time, churn, NPS and acquisition cost are excluded. Scores are prioritisation hints, not automated customer decisions. Recalibrate with time-based validation before any production use.

## Local state and limitations

- Assignments are local to the machine and stored in `runtime_ops.db`; they are not synced across devices or users.
- The source lead data is synthetic and covers one quarter. Dashboard results are descriptive, not causal evidence that the product changes conversion.
- The prototype has no authentication or role-based access control. Do not expose it to the public internet or load real customer data.
- The export includes synthetic business names and masked contact names; production exports require access controls and a formal retention policy.
