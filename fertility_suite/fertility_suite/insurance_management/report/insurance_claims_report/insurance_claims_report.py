import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"label": _("Claim"), "fieldname": "name", "fieldtype": "Link", "options": "Insurance Claim", "width": 110},
		{"label": _("Patient"), "fieldname": "patient", "fieldtype": "Link", "options": "Patient", "width": 130},
		{"label": _("Insurance Plan"), "fieldname": "insurance_plan", "fieldtype": "Link", "options": "Insurance Plan", "width": 140},
		{"label": _("Billing Type"), "fieldname": "billing_type", "fieldtype": "Data", "width": 100},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": _("Total Amount"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("Insurance Amount"), "fieldname": "insurance_amount", "fieldtype": "Currency", "width": 130},
		{"label": _("Patient Payable"), "fieldname": "patient_payable_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("Claim Date"), "fieldname": "claim_date", "fieldtype": "Date", "width": 100},
	]


def get_data(filters):
	conditions = ["1=1"]
	values = {}

	for field in ("status", "insurance_plan", "patient"):
		if filters.get(field):
			conditions.append(f"{field} = %({field})s")
			values[field] = filters[field]

	if filters.get("from_date"):
		conditions.append("claim_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions.append("claim_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]

	return frappe.db.sql(
		f"""
		select name, patient, insurance_plan, billing_type, status,
			   total_amount, insurance_amount, patient_payable_amount, claim_date
		from `tabInsurance Claim`
		where {' and '.join(conditions)}
		order by claim_date desc
		""",
		values,
		as_dict=True,
	)
