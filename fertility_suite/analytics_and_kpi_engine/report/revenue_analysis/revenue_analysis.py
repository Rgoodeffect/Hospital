import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"label": _("Month"), "fieldname": "month", "fieldtype": "Data", "width": 100},
		{"label": _("Claims"), "fieldname": "claim_count", "fieldtype": "Int", "width": 90},
		{"label": _("Total Billed"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("Insurance Covered"), "fieldname": "insurance_amount", "fieldtype": "Currency", "width": 140},
		{"label": _("Patient Payable"), "fieldname": "patient_payable_amount", "fieldtype": "Currency", "width": 130},
	]


def get_data(filters):
	conditions = ["1=1"]
	values = {}

	if filters.get("from_date"):
		conditions.append("claim_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions.append("claim_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]

	return frappe.db.sql(
		f"""
		select date_format(claim_date, '%%Y-%%m') as month,
			   count(*) as claim_count,
			   sum(total_amount) as total_amount,
			   sum(insurance_amount) as insurance_amount,
			   sum(patient_payable_amount) as patient_payable_amount
		from `tabInsurance Claim`
		where {' and '.join(conditions)}
		group by month
		order by month desc
		""",
		values,
		as_dict=True,
	)
