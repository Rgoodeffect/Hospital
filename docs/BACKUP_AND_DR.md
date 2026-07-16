# Backup Strategy & Disaster Recovery

Fertility Suite stores all of its data in the site's normal MariaDB database and the site's
`private`/`public` files directories (for attachments such as consent forms, ultrasound images,
lab reports) — there is no separate datastore to back up.

## What to back up

1. **Database** — `bench --site your-site.local backup --with-files` produces a timestamped SQL
   dump plus a tarball of the site's private/public files under `sites/your-site.local/private/backups/`.
2. **Site config** — `sites/your-site.local/site_config.json` (encryption key, DB credentials).
   Losing the encryption key makes encrypted fields (e.g. any password fields) unrecoverable even
   with a valid DB dump — back it up separately from the DB dump.
3. **Common site config** — `sites/common_site_config.json`.

## Recommended schedule

| What | Frequency | Retention |
|---|---|---|
| Full DB + files backup | Daily (off-peak) | 30 days rolling |
| `site_config.json` / encryption key | On every change | Indefinite, in a secrets manager |
| Off-site copy of backups | Daily | 90 days |

Automate with `bench` cron support (already enabled via `bench setup backups`, which schedules a
daily/hourly job through `scheduler_events` in Frappe core) or an external cron pushing the backup
directory to S3/Azure Blob/GCS with lifecycle rules.

## Docker Compose environments

Backups run inside the `backend` container, which shares the `fertility-sites` volume — mount
that volume (or `sites/*/private/backups`) to a host path or bind an S3-backed volume driver so
backups survive container recreation:

```bash
docker compose exec backend bench --site fertility.local backup --with-files
```

## Disaster recovery drill (recommended quarterly)

1. Provision a fresh environment (new Docker stack or bench).
2. Restore the latest backup:
   ```bash
   bench --site recovered.local restore /path/to/backup.sql.gz \
     --with-public-files /path/to/backup-files.tar \
     --with-private-files /path/to/backup-private-files.tar \
     --encryption-key <key from site_config.json>
   ```
3. Run `bench --site recovered.local migrate` to ensure schema matches the currently-installed
   app versions.
4. Smoke test: log in, open the Clinical/IVF/Embryology/Insurance/Executive workspaces, open a
   Fertility Case and an Embryo Inventory record, and confirm the Executive KPI Dashboard report
   renders.
5. Record time-to-restore against your RTO target and update this document if it changes.

## RPO/RTO targets (adjust to your clinic's requirements)

- **RPO (Recovery Point Objective):** ≤ 24 hours (daily backup cadence above). Reduce to hourly if
  the clinic's transaction volume justifies it — Frappe's backup scheduler supports this natively.
- **RTO (Recovery Time Objective):** ≤ 4 hours to a functioning site from a cold restore, assuming
  infrastructure (Docker/bench) can be reprovisioned in parallel with the data restore.
