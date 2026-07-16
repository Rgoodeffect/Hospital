import frappe
from frappe import _

CLOSED_STATUSES = ("Completed", "Cancelled")


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"label": _("Cycle"), "fieldname": "name", "fieldtype": "Link", "options": "IVF Cycle", "width": 120},
		{"label": _("Patient"), "fieldname": "patient", "fieldtype": "Link", "options": "Patient", "width": 150},
		{"label": _("Doctor"), "fieldname": "doctor", "fieldtype": "Link", "options": "Healthcare Practitioner", "width": 150},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
		{"label": _("Cycle Start Date"), "fieldname": "cycle_start_date", "fieldtype": "Date", "width": 120},
		{"label": _("Days In Cycle"), "fieldname": "days_in_cycle", "fieldtype": "Int", "width": 100},
	]


def get_data(filters):
	conditions = ["status not in %(closed_statuses)s"]
	values = {"closed_statuses": CLOSED_STATUSES}

	if filters.get("status"):
		conditions.append("status = %(status)s")
		values["status"] = filters["status"]

	if filters.get("doctor"):
		conditions.append("doctor = %(doctor)s")
		values["doctor"] = filters["doctor"]

	return frappe.db.sql(
		f"""
		select name, patient, doctor, status, cycle_start_date,
			   datediff(curdate(), cycle_start_date) as days_in_cycle
		from `tabIVF Cycle`
		where {' and '.join(conditions)}
		order by cycle_start_date desc
		""",
		values,
		as_dict=True,
	)
