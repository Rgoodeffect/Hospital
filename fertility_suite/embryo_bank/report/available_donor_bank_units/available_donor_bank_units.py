import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"label": _("Unit"), "fieldname": "name", "fieldtype": "Link", "options": "Donor Bank Unit", "width": 120},
		{"label": _("Donor"), "fieldname": "donor", "fieldtype": "Link", "options": "Gamete Donor", "width": 120},
		{"label": _("Unit Type"), "fieldname": "unit_type", "fieldtype": "Data", "width": 100},
		{"label": _("Blood Group"), "fieldname": "blood_group", "fieldtype": "Data", "width": 100},
		{"label": _("Quantity"), "fieldname": "quantity", "fieldtype": "Int", "width": 90},
		{"label": _("Grade"), "fieldname": "grade", "fieldtype": "Data", "width": 90},
		{"label": _("Tank"), "fieldname": "tank", "fieldtype": "Link", "options": "Storage Tank", "width": 100},
		{"label": _("Canister"), "fieldname": "canister", "fieldtype": "Link", "options": "Storage Canister", "width": 100},
		{"label": _("Freeze Date"), "fieldname": "freeze_date", "fieldtype": "Date", "width": 100},
	]


def get_data(filters):
	conditions = ["dbu.status = 'Available'"]
	values = {}
	if filters.get("unit_type"):
		conditions.append("dbu.unit_type = %(unit_type)s")
		values["unit_type"] = filters["unit_type"]
	if filters.get("blood_group"):
		conditions.append("gd.blood_group = %(blood_group)s")
		values["blood_group"] = filters["blood_group"]

	return frappe.db.sql(
		f"""
		select dbu.name, dbu.donor, dbu.unit_type, gd.blood_group, dbu.quantity, dbu.grade,
			   dbu.tank, dbu.canister, dbu.freeze_date
		from `tabDonor Bank Unit` dbu
		left join `tabGamete Donor` gd on gd.name = dbu.donor
		where {' and '.join(conditions)}
		order by dbu.freeze_date desc
		""",
		values,
		as_dict=True,
	)
