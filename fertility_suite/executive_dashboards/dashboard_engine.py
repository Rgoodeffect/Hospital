import frappe
from frappe.utils import add_days, today

CLOSED_CASE_STATUSES = ("Closed", "Cancelled")
CLOSED_CYCLE_STATUSES = ("Completed", "Cancelled")


@frappe.whitelist()
def generate_clinical_dashboard_snapshot():
	week_start = add_days(today(), -7)

	snapshot = frappe.get_doc({
		"doctype": "Clinical Dashboard Snapshot",
		"snapshot_date": today(),
		"active_fertility_cases": frappe.db.count(
			"Fertility Case", {"status": ["not in", CLOSED_CASE_STATUSES]}
		),
		"active_ivf_cycles": frappe.db.count(
			"IVF Cycle", {"status": ["not in", CLOSED_CYCLE_STATUSES]}
		),
		"monitoring_visits_today": frappe.db.count("Monitoring Visit", {"visit_date": today()}),
		"embryo_transfers_this_week": frappe.db.count(
			"Embryo Transfer", {"docstatus": 1, "transfer_date": ["between", [week_start, today()]]}
		),
		"pending_pregnancy_tests": frappe.db.count("IVF Cycle", {"status": "Pregnancy Test"}),
	})
	snapshot.insert(ignore_permissions=True)
	return snapshot.name


@frappe.whitelist()
def generate_weekly_executive_snapshot():
	from fertility_suite.analytics_and_kpi_engine.kpi_engine import (
		claim_approval_rate,
		collection_ratio,
		live_birth_rate,
		pregnancy_rate,
	)

	period_start = add_days(today(), -90)
	period_end = today()

	total_revenue = frappe.db.sql(
		"select sum(total_amount) from `tabInsurance Claim` where claim_date between %s and %s",
		(period_start, period_end),
	)[0][0] or 0

	snapshot = frappe.get_doc({
		"doctype": "Executive Dashboard Snapshot",
		"snapshot_date": today(),
		"active_patients": frappe.db.count(
			"Fertility Case", {"status": ["not in", CLOSED_CASE_STATUSES]}
		),
		"total_revenue": total_revenue,
		"pregnancy_rate": pregnancy_rate(period_start, period_end),
		"live_birth_rate": live_birth_rate(period_start, period_end),
		"claim_approval_rate": claim_approval_rate(period_start, period_end),
		"collection_ratio": collection_ratio(period_start, period_end),
	})
	snapshot.insert(ignore_permissions=True)
	return snapshot.name
