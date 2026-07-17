# UI Architecture

How the design system in [`design-system.md`](design-system.md) — extracted
from the Fertility & IVF Suite demo prototype — is actually wired into the
real ERPNext 16 + Healthcare + Fertility Suite implementation.

## 1. File inventory

| File | Role |
|---|---|
| `docs/design-system.md` | Source of truth: every color/font/spacing/component token, read directly off the demo's `style.css`/`app.js`. |
| `fertility_suite/public/css/fertility_suite.css` | Brand-level theme: overrides Frappe's own runtime CSS variables (`--primary-color`, `--btn-primary`, `--border-primary`, `--font-stack`) for both light and dark mode, app-wide (desk + website). |
| `fertility_suite/public/css/fertility_theme.css` | Component-level theme: badges/indicators, sidebar, navbar, workspace Number Cards, kanban, list rows, modals, print — one section per Frappe component, each selector verified against Frappe's own SCSS source for this version. |
| `fertility_suite/public/js/fertility_ui.js` | Additive only: animated count-up on workspace Number Cards (a `MutationObserver`, since workspaces re-render via Frappe's own router). Theme switching and sidebar collapse/expand are Frappe's own real features — not reimplemented. |
| `fertility_suite/www/login.py` / `login.html` / `login.css` | Branded login page (split-screen hero + real Frappe auth form), see the dedicated commit for how the override works. |
| `fertility_suite/www/fertility-portal.html` / `.py` / `.css` | Patient Portal, fully custom-controlled, themed 1:1 against the design system. |
| `fertility_suite/fixtures/number_card.json`, `dashboard_chart.json` | Real Frappe **Number Card** / **Dashboard Chart** records reproducing the demo's KPI/chart inventory, placed into workspaces. |
| `*/workspace/*/​*.json` | Workspace layouts (see §3) — number_card/chart/shortcut blocks. |

`hooks.py` wires all of the above via `app_include_css`, `app_include_js` and
`web_include_css` (desk + website) and the `fixtures` list (Number
Card/Dashboard Chart, alongside the existing Role/Workflow/Notification
Template fixtures).

## 2. What is themed vs. what is native Frappe

**Themed to match the demo (colors, fonts, radius, shadows, badges):**
sidebar, navbar, buttons, form inputs, workspace Number Cards, Dashboard
Charts, kanban board, list view rows/headers, modals, print heading, login
page, Patient Portal.

**Native Frappe, unmodified structure/behaviour:** list view filtering/
sorting/bulk actions, form validation/workflow/permissions, report builder,
kanban drag-and-drop, print format engine, real-time updates, file
attachments, the desk router itself. None of these are reimplemented —
doing so would mean giving up real ERPNext functionality, which was the
explicit constraint for this work.

## 3. Screenshot mapping matrix

Every real screen a user reaches, and which demo screen it is themed to match.

| Demo screen (`app.js` page id) | Real ERPNext location | Notes |
|---|---|---|
| Login | `/login` (custom template) | 1:1 rebuild: split-screen hero, same gradient/badge/stat treatment, real Frappe auth |
| Dashboard | Desk home / any Workspace | KPI row + chart row pattern (§5 of design-system.md) applied via Number Cards + Dashboard Charts |
| Executive Dashboard | **Executive** workspace | 4 Number Cards (Active Fertility Cases, Active IVF Cycles, Total Embryos, Pending Insurance Claims) + 2 Dashboard Charts (IVF Cycle Stage Distribution, Embryo Inventory Status) + report shortcuts (Doctor/Embryologist Performance, Pregnancy Outcomes) |
| Patients | ERPNext core **Patient** list (Healthcare module, unmodified) | Out of Fertility Suite's scope - core Healthcare doctype |
| Appointments | ERPNext core **Patient Appointment** list/calendar | Same |
| Fertility Cases | **Clinical** workspace → **Fertility Case** list | Number Card: Active Fertility Cases; shortcuts to Fertility Assessment, Treatment Plan, Active Fertility Cases report |
| IVF Cycles | **IVF** workspace → **IVF Cycle** list | Number Card: Active IVF Cycles; Chart: IVF Cycle Stage Distribution |
| Monitoring Visits | **IVF** workspace → **Monitoring Visit** list | Follicle/endometrium tracking fields on the doctype match the demo's monitoring table columns |
| Egg Retrieval | **IVF** workspace → **Egg Retrieval** list | |
| Embryology | **Embryology** workspace → **Embryology Record** list | Number Cards: Total Embryos, Frozen Embryos; Chart: Embryo Inventory Status |
| Embryo Bank | **Embryo Bank** workspace | Donor registry/screening/consent/storage/allocation (see the Embryo Bank feature work) |
| Embryo Transfer | **IVF** workspace → **Embryo Transfer** list | |
| Pregnancy Follow-up | **IVF** workspace → **Pregnancy Follow Up** list | |
| Insurance | **Insurance** workspace | Number Card: Pending Insurance Claims; shortcuts to Insurance Claims Report, Revenue Analysis |
| Finance / Revenue Analysis | **Insurance** workspace → **Revenue Analysis** report | The demo treats finance as part of the insurance/billing screen; no separate Frappe module owns billing outside Insurance Management + ERPNext Accounts, so this is not duplicated as its own workspace |

## 4. Known gap vs. a literal 95% pixel match

Frappe's list view, form view, kanban and report grid are rendered by
Frappe's own JS framework (not custom HTML we control). Every *visual
token* — color, font, radius, shadow, spacing, badge palette — is themed to
match the demo exactly (see `fertility_theme.css` for the selector-by-
selector mapping). What is **not** rebuilt is the literal DOM structure of
those native views (e.g. the demo's custom `<table class="table-hover">`
markup vs. Frappe's own `.list-row` grid, or the demo's custom search pill
vs. Frappe's awesomebar) — reproducing those pixel-for-pixel would mean
re-implementing Frappe's list/form rendering engine from scratch, which
would break real functionality (permissions, workflows, filters, bulk
actions, print, attachments) that this project explicitly needs to keep.
Pages that are **fully custom-controlled** (Login, Patient Portal) are themed
1:1. Pages **rendered by Frappe** (Desk list/form/kanban/report/print) match
the demo in every color/typography/spacing/badge/card/chart token, on top of
Frappe's own, unmodified interaction model.
