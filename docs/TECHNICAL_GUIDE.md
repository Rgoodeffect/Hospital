# Technical Guide

## App layout

Fertility Suite follows the standard Frappe app layout, with one folder per module (as declared
in `modules.txt`):

```
fertility_suite/fertility_suite/
  fertility_case_management/   Fertility Case
  fertility_assessment/        Fertility Assessment
  treatment_planning/          Treatment Plan
  ivf_cycle_management/        IVF Cycle
  follicle_monitoring/         Monitoring Visit, Follicle Measurement (child)
  egg_retrieval/                Egg Retrieval
  embryology_management/       Embryology Record
  embryo_inventory/             Embryo Inventory, Embryo Status Log (child)
  embryo_bank/                  Gamete Donor, Donor Screening, Donor Consent, Donor Bank Unit, Donor Allocation
  storage_tank_management/     Storage Tank, Storage Canister
  embryo_transfer/              Embryo Transfer, Embryo Transfer Item (child)
  pregnancy_follow_up/          Pregnancy Follow Up
  insurance_management/         Insurance Company, Insurance Plan, Pre Authorization, Insurance Claim
  analytics_and_kpi_engine/     KPI Snapshot + kpi_engine.py
  notification_engine/          Notification Template + notification_engine.py
  executive_dashboards/         Clinical/Executive Dashboard Snapshot + dashboard_engine.py
  patient_portal/               (portal pages live under www/, no dedicated DocTypes)
  api.py                        whitelisted REST-style endpoints
  hooks.py, modules.txt, patches.txt
  fixtures/                     Role, Workflow, Workflow State, Workflow Action Master, Notification Template
  setup/install.py              after_install / before_tests
  tests/test_utils.py           shared factory helpers for tests
```

## Design principles

- **No core modification.** Every hook into ERPNext/Healthcare core (currently just a client
  script on `Patient`) is additive, registered via `hooks.py` (`doctype_js`), never a direct edit
  to a core file.
- **Controllers own their lifecycle.** Every Fertility Suite DocType implements
  `validate`/`on_update`/`before_submit`/`on_submit` directly on its `Document` subclass rather
  than via `hooks.py: doc_events` — `doc_events` is reserved for hooking into doctypes this app
  does not own the controller of. This avoids the same validation running twice.
- **Fixtures over manual setup.** Roles, Workflows, Workflow States/Actions and Notification
  Templates all ship as fixtures (`fertility_suite/fixtures/*.json`) plus idempotent creation
  code in `setup/install.py`, so a fresh install and a `bench migrate` on an existing site both
  converge to the same state.

## Key business rules and where they live

| Rule | Location |
|---|---|
| One active Fertility Case per patient | `fertility_case_management/doctype/fertility_case/fertility_case.py::validate_case` |
| One active IVF Cycle per patient | `ivf_cycle_management/doctype/ivf_cycle/ivf_cycle.py::validate_cycle` |
| Mature Oocytes ≤ Retrieved Oocytes | `egg_retrieval/doctype/egg_retrieval/egg_retrieval.py::validate_retrieval` |
| Fertilized ≤ Mature; Blastocysts ≤ Day5+Day6 | `embryology_management/doctype/embryology_record/embryology_record.py` |
| No duplicate Tank/Canister/Straw/Position while occupied | `embryo_inventory/doctype/embryo_inventory/embryo_inventory.py::validate_inventory` |
| Embryo Inventory audit trail | `embryo_inventory/doctype/embryo_inventory/embryo_inventory.py::_record_status_transition` (writes to the `status_history` child table on every status change; combined with `track_changes=1` for full field-level Version history) |
| No transferring the same embryo twice | `embryo_transfer/doctype/embryo_transfer/embryo_transfer.py::before_submit` |
| Donor eligibility gate (screening passed + active consent + Active status) before a Donor Bank Unit can be made Available | `embryo_bank/doctype/donor_bank_unit/donor_bank_unit.py::validate_eligibility` |
| No duplicate Tank/Canister/Straw/Position for donor units (shares the same physical tanks as Embryo Inventory) | `embryo_bank/doctype/donor_bank_unit/donor_bank_unit.py::validate_unit`; occupancy is folded into `storage_tank.py::recompute_tank_usage` / `storage_canister.py::recompute_canister_usage` |
| A failed Donor Screening disqualifies the donor; a Withdrawal of Consent withdraws them and deactivates prior consents | `embryo_bank/doctype/gamete_donor/gamete_donor.py::recompute_screening_status` / `recompute_consent_status`, `embryo_bank/doctype/donor_consent/donor_consent.py::_withdraw_donor` |
| A Donor Allocation can only submit against an Available unit; cancelling one frees the unit again | `embryo_bank/doctype/donor_allocation/donor_allocation.py::before_submit` / `on_cancel` |
| Storage occupancy / nitrogen alerts | `storage_tank_management/doctype/storage_tank/storage_tank.py::check_alerts` (on save) + `check_all_tank_alerts` (hourly cron) |
| Insurance claim amount calculation | `insurance_management/doctype/insurance_claim/insurance_claim.py::calculate_claim` |
| KPI computation | `analytics_and_kpi_engine/kpi_engine.py` |

## Scheduled jobs (`hooks.py: scheduler_events`)

- Hourly: `storage_tank.check_all_tank_alerts`
- Daily: `kpi_engine.generate_daily_kpi_snapshot`, `dashboard_engine.generate_clinical_dashboard_snapshot`,
  `notification_engine.send_pregnancy_test_reminders`, `notification_engine.send_appointment_reminders`
- Weekly: `dashboard_engine.generate_weekly_executive_snapshot`

## API reference (`fertility_suite/api.py`)

All endpoints are `@frappe.whitelist()` and permission-checked (a Fertility Patient session is
always pinned to their own linked Patient record, regardless of any `patient` argument passed):

| Method | Purpose |
|---|---|
| `get_patient(patient=None)` | Patient master data |
| `get_fertility_cases(patient=None)` | List of Fertility Cases |
| `get_ivf_cycles(patient=None)` | List of IVF Cycles |
| `get_ivf_cycle_timeline(ivf_cycle)` | Cycle detail + follicle growth timeline |
| `get_embryo_inventory(patient=None)` | Embryo status list |
| `get_treatment_plans(patient=None)` | Treatment plan list |
| `get_insurance_claims(patient=None)` | Claims + computed amounts |
| `get_dashboard_kpis(kpi_names=None)` | Latest value per KPI Snapshot (desk users only) |

## Extending notifications

`notification_engine.notify(event, context, roles=None, users=None)` renders the active
Notification Template for `event` with the given Jinja context and fans it out across the
template's configured channels. To add a new event: add an option to `Notification Template.event`
(select field), add a `DEFAULT_TEMPLATES` entry in `notification_engine.py`, and call `notify(...)`
from wherever the event originates.
