import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"label": _("Embryo"), "fieldname": "name", "fieldtype": "Link", "options": "Embryo Inventory", "width": 110},
		{"label": _("Patient"), "fieldname": "patient", "fieldtype": "Link", "options": "Patient", "width": 130},
		{"label": _("IVF Cycle"), "fieldname": "ivf_cycle", "fieldtype": "Link", "options": "IVF Cycle", "width": 110},
		{"label": _("Stage"), "fieldname": "embryo_stage", "fieldtype": "Data", "width": 100},
		{"label": _("Grade"), "fieldname": "embryo_grade", "fieldtype": "Data", "width": 90},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": _("Tank"), "fieldname": "tank", "fieldtype": "Link", "options": "Storage Tank", "width": 100},
		{"label": _("Canister"), "fieldname": "canister", "fieldtype": "Link", "options": "Storage Canister", "width": 100},
		{"label": _("Straw"), "fieldname": "straw_number", "fieldtype": "Data", "width": 80},
		{"label": _("Position"), "fieldname": "position", "fieldtype": "Data", "width": 80},
		{"label": _("Freeze Date"), "fieldname": "freeze_date", "fieldtype": "Date", "width": 100},
	]


def get_data(filters):
	conditions = ["1=1"]
	values = {}

	for field in ("status", "embryo_stage", "tank", "ivf_cycle", "patient"):
		if filters.get(field):
			conditions.append(f"{field} = %({field})s")
			values[field] = filters[field]

	return frappe.db.sql(
		f"""
		select name, patient, ivf_cycle, embryo_stage, embryo_grade, status,
			   tank, canister, straw_number, position, freeze_date
		from `tabEmbryo Inventory`
		where {' and '.join(conditions)}
		order by modified desc
		""",
		values,
		as_dict=True,
	)
