"""Whitelisted REST-style API endpoints for Fertility Suite.

All endpoints go through frappe.client-style permission checks
(frappe.has_permission / get_list) so a Fertility Patient only ever sees
their own records, while staff roles see everything they're granted access
to via the DocType's standard permissions.
"""

import frappe
from frappe import _
from frappe.utils import add_days, today


def _resolve_patient(patient=None):
	"""Staff can pass an explicit patient; portal patients are pinned to
	their own linked Patient record regardless of what they pass."""
	user_roles = frappe.get_roles(frappe.session.user)

	if "Fertility Patient" in user_roles and "System Manager" not in user_roles:
		own_patient = frappe.db.get_value("Patient", {"user_id": frappe.session.user}, "name")
		if not own_patient:
			frappe.throw(_("No Patient record linked to your account"))
		return own_patient

	if not patient:
		frappe.throw(_("Patient is required"))
	return patient


@frappe.whitelist()
def get_patient(patient: str | None = None):
	patient = _resolve_patient(patient)
	frappe.has_permission("Patient", doc=patient, throw=True)
	return frappe.get_doc("Patient", patient).as_dict()


@frappe.whitelist()
def get_fertility_cases(patient: str | None = None):
	patient = _resolve_patient(patient)
	return frappe.get_list(
		"Fertility Case",
		filters={"patient": patient},
		fields=["name", "status", "doctor", "case_opened_on", "diagnosis"],
		order_by="case_opened_on desc",
	)


@frappe.whitelist()
def get_ivf_cycles(patient: str | None = None):
	patient = _resolve_patient(patient)
	return frappe.get_list(
		"IVF Cycle",
		filters={"patient": patient},
		fields=["name", "status", "doctor", "cycle_start_date", "trigger_date"],
		order_by="cycle_start_date desc",
	)


@frappe.whitelist()
def get_ivf_cycle_timeline(ivf_cycle: str):
	frappe.has_permission("IVF Cycle", doc=ivf_cycle, throw=True)

	from fertility_suite.follicle_monitoring.doctype.monitoring_visit.monitoring_visit import (
		get_follicle_growth_timeline,
	)

	cycle = frappe.get_doc("IVF Cycle", ivf_cycle)
	return {
		"cycle": cycle.as_dict(),
		"follicle_timeline": get_follicle_growth_timeline(ivf_cycle),
	}


@frappe.whitelist()
def get_embryo_inventory(patient: str | None = None):
	patient = _resolve_patient(patient)
	return frappe.get_list(
		"Embryo Inventory",
		filters={"patient": patient},
		fields=["name", "embryo_stage", "embryo_grade", "status", "freeze_date"],
		order_by="freeze_date desc",
	)


@frappe.whitelist()
def get_treatment_plans(patient: str | None = None):
	patient = _resolve_patient(patient)
	return frappe.get_list(
		"Treatment Plan",
		filters={"patient": patient},
		fields=["name", "protocol_type", "status", "start_date"],
		order_by="start_date desc",
	)


@frappe.whitelist()
def get_insurance_claims(patient: str | None = None):
	patient = _resolve_patient(patient)
	return frappe.get_list(
		"Insurance Claim",
		filters={"patient": patient},
		fields=[
			"name", "insurance_plan", "billing_type", "status", "total_amount",
			"insurance_amount", "patient_payable_amount", "claim_date",
		],
		order_by="claim_date desc",
	)


@frappe.whitelist()
def get_dashboard_kpis(kpi_names: list | None = None):
	"""Latest value for each requested KPI (or all KPIs if none given).
	Restricted to desk users with report access to KPI Snapshot."""
	frappe.has_permission("KPI Snapshot", throw=True)

	filters = {}
	if kpi_names:
		filters["kpi_name"] = ["in", kpi_names]

	snapshots = frappe.get_list(
		"KPI Snapshot",
		filters=filters,
		fields=["kpi_name", "dimension", "kpi_value", "snapshot_date"],
		order_by="snapshot_date desc",
		limit_page_length=0,
	)

	latest = {}
	for snap in snapshots:
		key = (snap.kpi_name, snap.dimension or "")
		if key not in latest:
			latest[key] = snap

	return list(latest.values())


@frappe.whitelist()
def get_command_center_kpis():
	"""The six headline KPIs for the Fertility Command Center dashboard."""
	period_end = today()
	period_start = add_days(period_end, -90)

	pregnancy_rate = frappe.db.get_value(
		"KPI Snapshot",
		{"kpi_name": "Pregnancy Rate", "dimension": ["is", "not set"]},
		"kpi_value",
		order_by="creation desc",
	) or 0

	revenue = frappe.db.sql(
		"select sum(total_amount) from `tabInsurance Claim` where claim_date between %s and %s",
		(period_start, period_end),
	)[0][0] or 0

	return {
		"total_patients": frappe.db.count("Patient"),
		"todays_appointments": frappe.db.count("Patient Appointment", {"appointment_date": today()}),
		"active_ivf_cycles": frappe.db.count("IVF Cycle", {"status": ["not in", ["Completed", "Cancelled"]]}),
		"pregnancy_rate": pregnancy_rate,
		"embryos_stored": frappe.db.count("Embryo Inventory", {"status": ["in", ["Frozen", "Stored"]]}),
		"revenue": revenue,
	}


@frappe.whitelist()
def get_command_center_charts():
	"""Chart.js-ready series for the Fertility Command Center dashboard."""
	period_end = today()
	period_start = add_days(period_end, -180)

	revenue_rows = frappe.db.sql(
		"""
		select date_format(claim_date, '%%Y-%%m') as month, sum(total_amount) as amount
		from `tabInsurance Claim`
		where claim_date between %s and %s
		group by month
		order by month
		""",
		(period_start, period_end),
		as_dict=True,
	)

	outcome_rows = frappe.db.sql(
		"""
		select outcome, count(*) as n
		from `tabPregnancy Follow Up`
		where outcome is not null and outcome != ''
		group by outcome
		""",
		as_dict=True,
	)

	embryo_rows = frappe.db.sql(
		"select status, count(*) as n from `tabEmbryo Inventory` group by status", as_dict=True
	)

	claim_rows = frappe.db.sql(
		"select status, count(*) as n from `tabInsurance Claim` group by status", as_dict=True
	)

	return {
		"revenue_trend": {
			"labels": [row.month for row in revenue_rows],
			"values": [float(row.amount or 0) for row in revenue_rows],
		},
		"ivf_success_rate": {
			"labels": [row.outcome for row in outcome_rows],
			"values": [row.n for row in outcome_rows],
		},
		"embryo_inventory": {
			"labels": [row.status for row in embryo_rows],
			"values": [row.n for row in embryo_rows],
		},
		"claims_status": {
			"labels": [row.status for row in claim_rows],
			"values": [row.n for row in claim_rows],
		},
	}
