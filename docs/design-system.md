# Fertility & IVF Suite — Design System

Extracted from the interactive prototype ("ERPNext Fertility & IVF Suite Demo" —
`index.html` / `style.css` / `app.js` / `charts.js`). This document is the single
source of truth for every visual decision applied to the real ERPNext 16 +
Healthcare + Fertility Suite implementation. Nothing here is a new design —
every value is read directly off the demo's own stylesheet.

## 1. Color Palette

### Brand
| Token | Value | Use |
|---|---|---|
| `--brand` | `#7c5cff` | Primary brand purple — buttons, links, active states, focus rings |
| `--brand-dark` | `#6a45f0` | Button hover/active |
| `--brand-soft` | `#efe9ff` | Light tints — active nav background, chip backgrounds |

### Accents
| Token | Value | Use |
|---|---|---|
| `--accent-teal` | `#00b8a9` | Embryology / lab accents, secondary series |
| `--accent-rose` | `#ff6b6b` | Alerts, negative deltas, danger |
| `--accent-amber` | `#ffa62b` | Revenue/finance accents, warning |
| `--accent-blue` | `#2f9bff` | Secondary brand gradient stop, info |

### Surfaces (light)
| Token | Value |
|---|---|
| `--bg-app` | `#f2f4fa` |
| `--bg-surface` | `#ffffff` |
| `--bg-subtle` | `#f7f8fc` |
| `--bg-sidebar` | `#171335` |
| `--bg-sidebar-active` | `rgba(124,92,255,.18)` |
| `--text-primary` | `#1c1f2e` |
| `--text-secondary` | `#6b7085` |
| `--text-muted` | `#9297ab` |
| `--border-color` | `#e7e9f2` |

### Surfaces (dark — `[data-theme="dark"]`)
| Token | Value |
|---|---|
| `--bg-app` | `#0f1120` |
| `--bg-surface` | `#171933` |
| `--bg-subtle` | `#1c1e3a` |
| `--bg-sidebar` | `#0b0c1c` |
| `--bg-sidebar-active` | `rgba(124,92,255,.28)` |
| `--text-primary` | `#eef0fb` |
| `--text-secondary` | `#a6abc7` |
| `--text-muted` | `#767aa0` |
| `--border-color` | `#2a2d4d` |

### Status colors (badges) — light / dark
| Meaning | Statuses using it | Light bg / text | Dark bg |
|---|---|---|---|
| Green (success) | Active, Completed, Approved, Paid, Scheduled, Euploid, Live Birth, Ongoing | `#e5f9f1` / `#0e9f6e` | `rgba(14,159,110,.18)` |
| Amber (pending) | Pending, Planned, Under Review, Submitted, Mosaic, Fresh-Pending | `#fef3e0` / `#b9770e` | `rgba(185,119,14,.2)` |
| Red (negative) | Cancelled, Rejected, No-show, Discarded, Aneuploid, Miscarriage, Not Pregnant | `#fde8e8` / `#e02424` | `rgba(224,36,36,.2)` |
| Blue (in-progress) | In Progress, Monitoring, Fertilization, Transfer, Frozen, Pregnant, Rising | `#e8f1ff` / `#2563eb` | `rgba(37,99,235,.22)` |
| Purple (on hold) | On Hold, Partially Approved | `#f1e8ff` / `#7c3aed` | `rgba(124,58,237,.22)` |
| Gray (closed/inactive) | Closed, Inactive, Discharged, Plateau/Falling | `#edeef2` / `#6b7085` | `rgba(255,255,255,.08)` |

Rule: color is derived from the **meaning of the status word**, not the doctype —
the same six-color system applies everywhere (patients, cases, cycles, embryos,
claims). Dark mode = `filter: brightness(1.25) saturate(1.1)` plus the
`rgba(...)` background swaps above.

## 2. Typography

- English: **Inter** (400/500/600/700/800)
- Arabic (`html[dir="rtl"]`): **Cairo** (same weights)
- Fallback stack: `"Segoe UI", "Tahoma", system-ui, -apple-system, sans-serif`
- Headings (`h1`–`h4`, KPI values): weight 700–800, tight letter-spacing (`-0.02em` on KPI values)
- Body: 400, `.87rem`–`.95rem`
- Labels/eyebrows (`.section-label`, table headers): `.68rem`–`.74rem`, uppercase, `letter-spacing: .06–.08em`, weight 700, `--text-muted`

## 3. Spacing & Layout Constants

| Token | Value |
|---|---|
| `--radius-lg` | 16px — cards, login card, modals |
| `--radius-md` | 12px — kpi icons, stat-mini, canister cards |
| `--radius-sm` | 8px — inputs, buttons, straw slots |
| `--sidebar-w` | 264px |
| `--topbar-h` | 64px |
| `--shadow-card` | `0 2px 10px rgba(31,35,75,.06)` (dark: `0 2px 14px rgba(0,0,0,.35)`) |
| `--shadow-elevated` | `0 12px 30px rgba(31,35,75,.12)` (dark: `0 16px 40px rgba(0,0,0,.5)`) |
| Content padding | `1.6rem` (`.content-area`) |
| Grid gutter | `.9rem`–`1rem` (`row g-3` = Bootstrap 0.75rem, tank/canister grids `.7–.9rem`) |

## 4. Cards

`.card`: `bg-surface` + `1px solid border-color` + `radius-lg` + `shadow-card`.
Two specialised variants:

- **KPI card** (`.kpi-card`): icon chip (44×44, `radius-md`, gradient fill, white icon) → value (1.7rem/800) → label (`.8rem`, secondary) → delta (`.76rem/600`, green `↑` / rose `↓`).
- **Stat mini** (`.stat-mini`): `bg-subtle`, `radius-md`, centered, value 1.3rem/800 + label `.74rem` secondary. Used for compact inline stat rows (retrieval counts, embryo totals).

## 5. Dashboard Layout

Grid pattern used on every dashboard-style page (Dashboard, Executive, Retrieval, Insurance):
1. **Header row** — title + subtitle/breadcrumb left, action buttons right (`.page-header`).
2. **KPI row** — `row g-3`, 6 cards on Dashboard (`col-6 col-lg-4 col-xl-2`), 4 on Executive/module pages (`col-6 col-lg-3`).
3. **Chart row** — `row g-3`, typically a 7/5 or 6/6 split: one larger trend/line chart + one doughnut/breakdown chart, each in its own `.card.p-3` with a `.section-label` and a `.chart-box` (fixed height 260px, `.sm` = 190px).
4. **Detail row** — two-column list/table cards (recent records left ~58%, upcoming/secondary list right ~42%).

## 6. Sidebar

Dark sidebar (`--bg-sidebar`), fixed width 264px, full height, sticky.
Structure top→bottom:
1. **Brand block** (`.sidebar-brand`) — 38×38 gradient mark (brand→accent-blue) + app name (bold, .95rem) + subtitle (.7rem, muted) — bottom border `rgba(255,255,255,.08)`.
2. **Nav sections**, each a `.nav-section-title` (uppercase eyebrow) followed by `.nav-link` rows (icon 18px + label, `.87rem`). Active state: `--bg-sidebar-active` fill + 3px solid brand left border (right border in RTL) + icon/text turn brand-colored.
3. **Footer** (`.sidebar-footer`) — pinned to bottom, `.74rem`, muted, version/build label.

Section → item map (this is the canonical nav grouping to mirror in ERPNext workspaces):

| Section | Items |
|---|---|
| Overview | Dashboard, Executive Dashboard |
| Patient Care | Patients, Appointments |
| Fertility & IVF | Fertility Cases, IVF Cycles, Monitoring Visits, Egg Retrieval |
| Embryology Lab | Embryology, Embryo Bank, Embryo Transfer |
| Outcomes | Pregnancy Follow-up |
| Finance | Insurance Management |

Mobile (`<991px`): sidebar becomes a fixed off-canvas drawer (`transform: translateX(-110%)`, RTL mirrors to `+110%`), toggled by a hamburger button + dark overlay.

## 7. Navigation / Topbar

64px fixed header: hamburger (mobile only) + current-page label → search box (pill, `radius: 30px`, icon inset) → icon buttons (theme toggle, language toggle, notification bell with rose dot) → user chip (avatar circle + name/role + chevron, opens dropdown: Profile / Settings / divider / Log out).

## 8. Buttons

- `.btn` base: `radius-sm`, `.85rem`, weight 600.
- `.btn-brand`: gradient `brand → brand-dark`, white text; hover lifts `-1px` + purple glow shadow `0 8px 18px rgba(124,92,255,.35)`.
- `.btn-light-brand`: `brand-soft` bg / brand text; hover inverts to solid brand. Dark mode: `rgba(124,92,255,.18)` bg, `#cbb9ff` text.
- `.btn-outline-soft`: 1px border-color, secondary text, surface bg; hover fills `bg-subtle`.

## 9. Forms

Inputs (`.form-control`, `.form-select`): `bg-subtle`, `1px solid border-color`, `radius-sm`, `.65rem .9rem` padding. Focus: border turns brand, `box-shadow: 0 0 0 3px rgba(124,92,255,.18)` (no default browser outline). Labels: small, semibold, above field. Modals reuse the same field styling inside a `.modal-content` themed to `bg-surface`/`border-color`/`radius-lg`.

## 10. Tables

`.table-card` (a `.card` with `padding:0`): toolbar (search + filters left, record count + primary action right) → `thead` uppercase `.74rem` secondary text on `bg-subtle` → body rows `.87rem`, `1px` row dividers, hover → `bg-subtle` + pointer cursor when row is clickable → footer toolbar (showing X–Y of N + prev/page/next).

## 11. Badges / Status Pills

`.badge-soft`: `.72rem/600`, `radius: 20px`, `.38rem .65rem` padding — color per the status table in §1. This is the **only** status-representation pattern in the whole product (list rows, detail headers, timelines all reuse it).

## 12. KPI Widgets & Charts (Chart.js)

Palette (`SERIES`): brand, teal, blue, amber, rose, purple, green, grey — always in that order for consistent series coloring across every chart. All charts share `baseOptions()`: transparent grid on the x-axis, subtle grid (`rgba(31,35,75,.06)` / dark `rgba(255,255,255,.06)`) on y, legend text colored via `textColor()` (secondary text color, theme-aware), tooltip background `#1c1f2e`/`#232548`.

Chart inventory (page → chart type → data):
| Page | Charts |
|---|---|
| Dashboard | Line: new cycles/12mo · Doughnut: cycle stage distribution |
| Executive | Bar: fertilization funnel (oocytes→fertilized→blastocyst→transferred) · Line: revenue vs. insurance collections/12mo · Doughnut: embryo grade dist · Doughnut: pregnancy outcome dist · Pie: cycle stage dist |
| Monitoring | Dual-axis line: avg follicle size (mm) vs. endometrium thickness (mm), per visit |
| Retrieval | Horizontal bar: MII / MI / GV / Atretic counts |
| Embryology | Bar: embryo count by grade · Doughnut: final status distribution |
| Pregnancy | Pie: outcome distribution |
| Insurance | Bar: revenue by provider · Doughnut: claim status distribution |

KPI cards always: colored gradient icon chip → animated counter (count-up over ~30 steps) → label → delta (↑/↓ + %, or a plain secondary caption for non-directional stats like "N pending claims").

## 13. Icons

Font Awesome 6 (solid style, `fa-solid`). One icon per nav item/KPI, semantically matched (`fa-hospital-user` patients, `fa-arrows-spin` cycles, `fa-snowflake` embryo bank/frozen, `fa-dna` brand mark, `fa-microscope` embryology, `fa-file-invoice-dollar` insurance, `fa-baby` pregnancy).

## 14. Specialised Widgets

- **Cycle tracker** (`.cycle-tracker`): horizontal step timeline, each step a dot (34px circle) + connecting line + label; done = filled brand, current = white w/ brand ring + halo shadow, upcoming = subtle/muted.
- **Vertical timeline** (`.timeline-vert`): left border rail + dot markers per history entry.
- **Embryo Bank tank/canister/straw grid**: drill-down cards (tank → canister → straw), straw slots are a 5-col grid of small squares, occupied = teal gradient + snowflake icon, empty = subtle + hover brand outline.
- **Grade chip** (`.grade-chip`): small pill, brand-soft bg/brand text, bold — used for embryo grading (AA, AB, BB…).
- **Calendar grid**: 7-col CSS grid, `1px` hairlines via grid-gap on border-color, today = inset brand ring, events = small brand-soft pills truncated with ellipsis.

## 15. Modals

Bootstrap modal, restyled: `bg-surface`, `1px solid border-color`, `radius-lg`; header/footer borders use `border-color`. Same input/button styling as the rest of the app — no visual break between page and modal.

## 16. Responsive Behavior

Breakpoint: `991px`. Below it: sidebar off-canvas (see §6), search box hidden from topbar, KPI cards drop from 6/4-per-row to 2-per-row (`col-6`), charts and grids reflow to single/double column.

## 17. Dark Mode / Light Mode

Toggled via `[data-theme="dark"|"light"]` on `<html>`, persisted in `localStorage`. Every color token in §1 has a dark counterpart; component rules generally reference the token (`var(--bg-surface)` etc.) so no component-level dark overrides are needed except: badges (brightness/saturate filter + rgba swap), icon-button hover tint, tracker "current" halo, canister-card hover, grade-chip, calendar event pill. Charts re-read `textColor()`/`gridColor()` from the current theme on every re-render.

## 18. RTL / Language

`html[dir="rtl"]` flips: sidebar off-canvas direction, `border-inline-start` (used everywhere instead of literal left/right) for active-nav/timeline rails, topbar user-chip padding, icon-button "dot" badge position via logical `inset-inline-*` properties throughout — so the whole system is written in logical (not physical) CSS properties, which is what makes RTL "free". Font swaps to Cairo. Status/label text is looked up from an `en → ar` dictionary (`STATUS_AR`) rather than re-styled.

---

## How this maps onto the real ERPNext 16 implementation

Frappe's Desk (list views, form views, sidebar tree, kanban, print, reports) is
rendered by Frappe's own framework — we do not re-implement that renderer.
Instead:

1. Every color/typography/spacing/radius/shadow token above is applied via
   Frappe's own themeable CSS custom properties
   (`frappe/public/scss/common/css_variables.scss`,
   `frappe/public/scss/desk/dark.scss`) plus targeted component overrides in
   `fertility_suite/public/css/fertility_theme.css` — see that file for the
   exact selector-by-selector mapping (Frappe class → demo pattern).
2. Status badges: Frappe's own `.indicator-pill` system is re-colored to the
   same six-bucket palette in §1 (rather than inventing a parallel system).
3. Dashboards/KPIs: real Frappe **Number Card** and **Dashboard Chart**
   documents are created per workspace, configured to match the KPI/chart
   inventory in §12 (see `docs/ui-architecture.md` for the full
   page-by-page mapping).
4. The Patient Portal (`fertility_suite/www/fertility-portal.html`) is fully
   custom-controlled HTML, so it is themed 1:1 against this document with no
   framework constraint.
5. The Login page (`fertility_suite/www/login.html`) already implements the
   split-screen hero pattern described in the demo's login screen, using the
   same gradient/badge/stat treatment as §1–§3.
