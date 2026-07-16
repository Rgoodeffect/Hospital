# Fertility Suite

معالجة العقم ومشاكل الخصوبة ومتابعة أطفال الأنابيب

A production-ready [ERPNext 16](https://github.com/frappe/erpnext) application that extends the
Healthcare module into a complete **Fertility, IVF, Embryology and Embryo Bank Management System**.

Fertility Suite never modifies ERPNext core or the Healthcare module — every DocType, workflow,
report, dashboard and script lives inside the `fertility_suite` app and layers on top via hooks,
fixtures and whitelisted APIs.

## Modules

1. Fertility Case Management
2. Fertility Assessment
3. Treatment Planning
4. IVF Cycle Management
5. Follicle Monitoring
6. Egg Retrieval
7. Embryology Management
8. Embryo Inventory
9. Embryo Bank
10. Storage Tank Management
11. Embryo Transfer
12. Pregnancy Follow-up
13. Insurance Management
14. Patient Portal
15. Executive Dashboards
16. Analytics & KPI Engine
17. Notification Engine

## Documentation

| Guide | Description |
|---|---|
| [docs/INSTALLATION.md](docs/INSTALLATION.md) | Bench/Docker installation steps |
| [docs/ADMINISTRATOR_GUIDE.md](docs/ADMINISTRATOR_GUIDE.md) | Roles, workflows, configuration |
| [docs/USER_GUIDE.md](docs/USER_GUIDE.md) | Day-to-day clinical/embryology workflow |
| [docs/TECHNICAL_GUIDE.md](docs/TECHNICAL_GUIDE.md) | DocType/API/architecture reference |
| [docs/MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md) | Upgrading between versions |
| [docs/BACKUP_AND_DR.md](docs/BACKUP_AND_DR.md) | Backup strategy & disaster recovery |

## Quick start (Docker)

```bash
cp .env.example .env
docker compose up -d
```

See [docs/INSTALLATION.md](docs/INSTALLATION.md) for the full bench-based install and for running
against an existing ERPNext/Healthcare site.

## Running tests

```bash
bench --site fertility.local run-tests --app fertility_suite
```

## License

MIT
