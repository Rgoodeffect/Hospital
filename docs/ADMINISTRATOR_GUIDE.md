# Administrator Guide

## Roles

| Role | Typical user | Desk access |
|---|---|---|
| Fertility Doctor | Reproductive endocrinologist / IVF physician | Yes |
| Embryologist | Lab staff performing fertilization, culture, freezing | Yes |
| IVF Coordinator | Nurse/coordinator managing cycle logistics | Yes |
| Fertility Nurse | Clinical support staff | Yes |
| Insurance Officer | Billing / insurance desk | Yes |
| Clinic Manager | Operations manager, approves workflows, sees KPIs | Yes |
| Fertility Patient | The patient themself | No (portal only, via `/fertility-portal`) |

Roles are installed automatically (`fertility_suite/setup/install.py`) and also ship as a fixture
(`fertility_suite/fixtures/role.json`) so they survive `bench migrate` on fresh sites pulled from
this repo. Assign roles to staff under **User List > (user) > Roles**.

## Workflows

Three DocTypes are workflow-driven (`fertility_suite/fixtures/workflow.json`):

- **Fertility Case Workflow**: Draft → Assessment → Treatment → IVF Active → Pregnant → Closed,
  with Cancel available from any non-terminal state. Transitions are gated by role (Fertility
  Doctor drives clinical progression; Clinic Manager closes/cancels).
- **Treatment Plan Workflow**: Draft → Review → Approved → Active → Completed (with a Reject path
  back to Draft from Review).
- **IVF Cycle Workflow**: Planned → Stimulation → Monitoring → Trigger → Retrieval →
  Fertilization → Embryology → Transfer → Pregnancy Test → Completed, with Cancel available from
  the early/mid stages. Fertilization/Embryology transitions are restricted to the Embryologist
  role; clinical transitions to Fertility Doctor.

All three workflows point `workflow_state_field` at the DocType's own `status` Select field
rather than adding a separate hidden `workflow_state` field, since `status` already carries
exactly the state names used by the workflow.

Workflows can be edited from **Workflow** list in the desk like any other Frappe workflow; changes
you make there will NOT be overwritten by `bench migrate` unless you re-export the fixture.

## Storage Tank alerts

Every **Storage Tank** carries `occupancy_alert_threshold` (default 90%) and `nitrogen_threshold`
(default 20%). An hourly cron job (`storage_tank.check_all_tank_alerts`) and the tank's own
`on_update` hook recompute occupancy/nitrogen state and fire a "Storage Tank Alert" notification
(System Notification + Email + Push, by default) to the Embryologist and Clinic Manager roles
whenever a threshold is crossed. Adjust the thresholds per-tank, or edit the "Storage Tank Alert"
Notification Template to change channels/wording.

## Notification Templates

**Notification Engine > Notification Template** holds one record per event (Appointment
Reminder, Lab Result Ready, Claim Approved, Cycle Started, Embryo Transfer Scheduled, Pregnancy
Test Reminder, Storage Tank Alert). Each has a `channels` multi-select (Email / SMS / WhatsApp /
System Notification / Push Notification) and a Jinja-templated subject/message. Disable a
template with its `disabled` checkbox to silence that event entirely.

SMS and WhatsApp channels are wired to `dispatch_sms`/`dispatch_whatsapp` in
`notification_engine.py`, which currently just log the outbound message — replace the body of
`_send_sms_via_gateway`/`_send_whatsapp_via_gateway` with a call to your provider (Twilio, Meta
Cloud API, a local aggregator, etc.).

## KPIs and Dashboards

`analytics_and_kpi_engine.kpi_engine.generate_daily_kpi_snapshot` runs daily and writes **KPI
Snapshot** rows for: Pregnancy Rate, Clinical Pregnancy Rate, Live Birth Rate, Fertilization Rate,
Blastocyst Rate, Claim Approval Rate, Collection Ratio, Revenue per Doctor (one row per doctor),
and Revenue per Treatment Type (one row per protocol). All rates are computed over a trailing
90-day window (`DEFAULT_WINDOW_DAYS`).

`executive_dashboards.dashboard_engine` additionally writes a **Clinical Dashboard Snapshot**
daily and an **Executive Dashboard Snapshot** weekly, so the Executive workspace loads
instantaneously instead of aggregating live on every page view.

## Permissions model

Fertility Case, IVF Cycle and Embryo Inventory each register a
`permission_query_conditions`/`has_permission` pair (see `hooks.py`) that restricts a user with
only the Fertility Patient role to rows where `patient` matches the Patient record linked to
their User (`Patient.user_id`). Staff roles are unaffected and see records per the DocType's
normal role-based permissions.
