"""Computes the clinic-wide KPIs listed in the Fertility Suite spec and
persists them as KPI Snapshot records so dashboards can read pre-aggregated
values instead of running expensive queries on every page load.

Rates are computed over a rolling trailing window (default 90 days) ending
on the snapshot date, which is the standard way fertility clinics report
these metrics since cycle outcomes lag the cycle itself by weeks.
"""

import frappe
from frappe.utils import add_days, today

DEFAULT_WINDOW_DAYS = 90


@frappe.whitelist()
def generate_daily_kpi_snapshot(window_days: int = DEFAULT_WINDOW_DAYS):
	period_end = today()
	period_start = add_days(period_end, -window_days)

	values = {
		"Pregnancy Rate": pregnancy_rate(period_start, period_end),
		"Clinical Pregnancy Rate": clinical_pregnancy_rate(period_start, period_end),
		"Live Birth Rate": live_birth_rate(period_start, period_end),
		"Fertilization Rate": fertilization_rate(period_start, period_end),
		"Blastocyst Rate": blastocyst_rate(period_start, period_end),
		"Claim Approval Rate": claim_approval_rate(period_start, period_end),
		"Collection Ratio": collection_ratio(period_start, period_end),
	}

	for kpi_name, value in values.items():
		_upsert_snapshot(kpi_name, None, value, period_start, period_end)

	for dimension, value in revenue_per_doctor(period_start, period_end).items():
		_upsert_snapshot("Revenue per Doctor", dimension, value, period_start, period_end)

	for dimension, value in revenue_per_treatment_type(period_start, period_end).items():
		_upsert_snapshot("Revenue per Treatment Type", dimension, value, period_start, period_end)

	return values


def _upsert_snapshot(kpi_name, dimension, value, period_start, period_end):
	frappe.get_doc({
		"doctype": "KPI Snapshot",
		"kpi_name": kpi_name,
		"dimension": dimension,
		"snapshot_date": today(),
		"period_start": period_start,
		"period_end": period_end,
		"kpi_value": value or 0,
	}).insert(ignore_permissions=True)


def _ratio(numerator, denominator):
	return round((numerator / denominator) * 100, 2) if denominator else 0


def pregnancy_rate(period_start, period_end):
	transfers = frappe.db.count(
		"Embryo Transfer", {"docstatus": 1, "transfer_date": ["between", [period_start, period_end]]}
	)
	pregnancies = frappe.db.count(
		"Pregnancy Follow Up",
		{
			"outcome": ["in", ["Clinical Pregnancy", "Ongoing Pregnancy", "Live Birth"]],
			"follow_up_date": ["between", [period_start, period_end]],
		},
	)
	return _ratio(pregnancies, transfers)


def clinical_pregnancy_rate(period_start, period_end):
	tested = frappe.db.count(
		"Pregnancy Follow Up",
		{"outcome": ["!=", ""], "follow_up_date": ["between", [period_start, period_end]]},
	)
	clinical = frappe.db.count(
		"Pregnancy Follow Up",
		{
			"outcome": ["in", ["Clinical Pregnancy", "Ongoing Pregnancy", "Live Birth"]],
			"follow_up_date": ["between", [period_start, period_end]],
		},
	)
	return _ratio(clinical, tested)


def live_birth_rate(period_start, period_end):
	transfers = frappe.db.count(
		"Embryo Transfer", {"docstatus": 1, "transfer_date": ["between", [period_start, period_end]]}
	)
	live_births = frappe.db.count(
		"Pregnancy Follow Up",
		{"outcome": "Live Birth", "follow_up_date": ["between", [period_start, period_end]]},
	)
	return _ratio(live_births, transfers)


def fertilization_rate(period_start, period_end):
	row = frappe.db.sql(
		"""
		select sum(er.fertilized_oocytes) as fertilized, sum(eg.mature_oocytes) as mature
		from `tabEmbryology Record` er
		left join `tabEgg Retrieval` eg on eg.name = er.egg_retrieval
		where er.fertilization_date between %s and %s
		""",
		(period_start, period_end),
		as_dict=True,
	)
	if not row or not row[0].mature:
		return 0
	return _ratio(row[0].fertilized or 0, row[0].mature)


def blastocyst_rate(period_start, period_end):
	row = frappe.db.sql(
		"""
		select sum(blastocysts) as blastocysts, sum(fertilized_oocytes) as fertilized
		from `tabEmbryology Record`
		where fertilization_date between %s and %s
		""",
		(period_start, period_end),
		as_dict=True,
	)
	if not row or not row[0].fertilized:
		return 0
	return _ratio(row[0].blastocysts or 0, row[0].fertilized)


def claim_approval_rate(period_start, period_end):
	submitted = frappe.db.count(
		"Insurance Claim",
		{"status": ["!=", "Draft"], "claim_date": ["between", [period_start, period_end]]},
	)
	approved = frappe.db.count(
		"Insurance Claim",
		{
			"status": ["in", ["Approved", "Partially Approved", "Paid"]],
			"claim_date": ["between", [period_start, period_end]],
		},
	)
	return _ratio(approved, submitted)


def collection_ratio(period_start, period_end):
	row = frappe.db.sql(
		"""
		select sum(total_amount) as total, sum(insurance_amount + (total_amount - insurance_amount - co_payment_amount)) as billed
		from `tabInsurance Claim`
		where status = 'Paid' and claim_date between %s and %s
		""",
		(period_start, period_end),
		as_dict=True,
	)
	if not row or not row[0].total:
		return 0
	return _ratio(row[0].billed or 0, row[0].total)


def revenue_per_doctor(period_start, period_end):
	rows = frappe.db.sql(
		"""
		select fc.doctor as doctor, sum(ic.total_amount) as revenue
		from `tabInsurance Claim` ic
		inner join `tabFertility Case` fc on fc.name = ic.fertility_case
		where ic.claim_date between %s and %s
		group by fc.doctor
		""",
		(period_start, period_end),
		as_dict=True,
	)
	return {row.doctor: row.revenue for row in rows if row.doctor}


def revenue_per_treatment_type(period_start, period_end):
	rows = frappe.db.sql(
		"""
		select tp.protocol_type as protocol_type, sum(ic.total_amount) as revenue
		from `tabInsurance Claim` ic
		inner join `tabTreatment Plan` tp on tp.fertility_case = ic.fertility_case
		where ic.claim_date between %s and %s
		group by tp.protocol_type
		""",
		(period_start, period_end),
		as_dict=True,
	)
	return {row.protocol_type: row.revenue for row in rows if row.protocol_type}
