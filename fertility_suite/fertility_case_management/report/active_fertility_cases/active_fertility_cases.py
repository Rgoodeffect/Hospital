import frappe
from frappe import _

CLOSED_STATUSES = ("Closed", "Cancelled")


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"label": _("Case"), "fieldname": "name", "fieldtype": "Link", "options": "Fertility Case", "width": 120},
		{"label": _("Patient"), "fieldname": "patient", "fieldtype": "Link", "options": "Patient", "width": 150},
		{"label": _("Patient Name"), "fieldname": "patient_name", "fieldtype": "Data", "width": 150},
		{"label": _("Doctor"), "fieldname": "doctor", "fieldtype": "Link", "options": "Healthcare Practitioner", "width": 150},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": _("Case Opened On"), "fieldname": "case_opened_on", "fieldtype": "Date", "width": 120},
		{"label": _("Days Open"), "fieldname": "days_open", "fieldtype": "Int", "width": 90},
	]


def get_data(filters):
	conditions = ["status not in %(closed_statuses)s"]
	values = {"closed_statuses": CLOSED_STATUSES}

	if filters.get("doctor"):
		conditions.append("doctor = %(doctor)s")
		values["doctor"] = filters["doctor"]

	if filters.get("status"):
		conditions.append("status = %(status)s")
		values["status"] = filters["status"]

	rows = frappe.db.sql(
		f"""
		select name, patient, patient_name, doctor, status, case_opened_on,
			   datediff(curdate(), case_opened_on) as days_open
		from `tabFertility Case`
		where {' and '.join(conditions)}
		order by case_opened_on desc
		""",
		values,
		as_dict=True,
	)
	return rows
