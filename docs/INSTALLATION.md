# Installation Guide

Fertility Suite is a Frappe app that extends ERPNext 16's Healthcare module. It never modifies
ERPNext or Healthcare core, so it can be installed onto any existing ERPNext + Healthcare site.

## Option A: Docker (recommended for evaluation / production)

Requirements: Docker Engine 24+, Docker Compose v2, 4 GB+ RAM.

```bash
git clone https://github.com/rgoodeffect/hospital.git fertility-suite
cd fertility-suite
cp .env.example .env
# edit .env: set SITE_NAME, ADMIN_PASSWORD, DB_ROOT_PASSWORD
docker compose build
docker compose up -d
```

The `configurator` service waits for MariaDB/Redis, creates the site named in `SITE_NAME`, and
installs `erpnext`, `healthcare`, and `fertility_suite` on it automatically the first time the
stack comes up. Subsequent `docker compose up` runs are idempotent (it skips site creation if the
site directory already exists).

Once containers are healthy, the app is available at `http://localhost:${BACKEND_PORT}` (default
`8000`), logging in as `Administrator` / the password you set in `ADMIN_PASSWORD`.

## Option B: Existing bench (bare metal / VM)

Requirements: a working [Frappe Bench](https://github.com/frappe/bench) with Frappe 16 and
ERPNext 16 already set up, Python 3.12+, MariaDB, Redis, Node.js/Yarn per the standard Frappe
requirements.

```bash
cd frappe-bench

# Healthcare is a prerequisite - install it first if you haven't already
bench get-app healthcare https://github.com/frappe/health --branch version-16
bench --site your-site.local install-app healthcare

# Fertility Suite
bench get-app fertility_suite https://github.com/rgoodeffect/hospital --branch main
bench --site your-site.local install-app fertility_suite

bench --site your-site.local migrate
bench restart
```

`install-app` runs `fertility_suite/setup/install.py:after_install`, which creates the app's
custom roles (Fertility Doctor, Embryologist, IVF Coordinator, Fertility Nurse, Insurance
Officer, Clinic Manager, Fertility Patient) and seeds the default Notification Templates.
Workflows, Workflow States/Actions and Roles also ship as fixtures under
`fertility_suite/fixtures/` and sync automatically on `bench migrate`.

## Post-install checklist

1. Log in as Administrator and open the **Clinical**, **IVF**, **Embryology**, **Insurance** and
   **Executive** workspaces (left sidebar) to confirm they loaded.
2. Create at least one **Healthcare Practitioner** and one **Patient** (standard Healthcare
   doctypes) before creating your first **Fertility Case**.
3. Assign the Fertility Suite roles to your staff users under **User** > Roles.
4. For patients who should get portal access, set **Patient.user_id** to a User account with the
   **Fertility Patient** role, then send them to `/fertility-portal`.
5. Configure an **Email Account** (Settings > Email Account) so Notification Template emails can
   send; wire `dispatch_sms`/`dispatch_whatsapp` in
   `fertility_suite/notification_engine/notification_engine.py` to your SMS/WhatsApp gateway of
   choice (they're stubbed to a log line out of the box).
6. Run `bench --site your-site.local execute fertility_suite.analytics_and_kpi_engine.kpi_engine.generate_daily_kpi_snapshot`
   once to seed initial KPI Snapshots for the Executive workspace.

## Running the test suite

```bash
bench --site your-site.local run-tests --app fertility_suite
```

See the main [README](../README.md) for a summary of what's covered.
