# Migration Guide

## Upgrading Fertility Suite on an existing site

```bash
cd frappe-bench
bench get-app fertility_suite --branch main  # pulls latest into apps/fertility_suite
bench --site your-site.local migrate
bench restart
```

`bench migrate` will:

1. Run any new patches listed in `fertility_suite/patches.txt`.
2. Sync DocType schema changes (new/changed fields, new DocTypes).
3. Re-sync fixtures (`fertility_suite/fixtures/*.json`) — Roles, Workflows, Workflow
   States/Actions, Notification Templates.

## Adding a new patch

1. Create `fertility_suite/patches/v1_1/<patch_name>.py` with an `execute()` function.
2. Add its dotted path to `fertility_suite/patches.txt` under `[post_model_sync]` (or
   `[pre_model_sync]` if it must run before DocType schema sync, e.g. to migrate data out of a
   field that's about to be removed).
3. Patches must be idempotent — `bench migrate` may be re-run after a partial failure.

## Version compatibility

Fertility Suite targets **ERPNext 16 / Frappe Framework 16** and the `develop` branch of
`frappe/health` (Healthcare). `required_apps` in `hooks.py` (`frappe`, `erpnext`, `healthcare`)
is enforced by `bench install-app` — installing on a site without Healthcare will fail fast with
a clear error rather than partially installing.

## Rolling back

Frappe does not support automatic downgrade of DocType schema. To roll back:

1. Restore the database backup taken before the upgrade (see
   [BACKUP_AND_DR.md](BACKUP_AND_DR.md)).
2. `bench switch-to-branch <previous-tag> fertility_suite` (or reinstall the previous release).
3. `bench --site your-site.local migrate`.

Always take a full backup (`bench --site your-site.local backup --with-files`) immediately before
running `bench update` or `bench migrate` in production.
