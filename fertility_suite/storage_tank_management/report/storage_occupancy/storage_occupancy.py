import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"label": _("Tank"), "fieldname": "name", "fieldtype": "Link", "options": "Storage Tank", "width": 100},
		{"label": _("Location"), "fieldname": "location", "fieldtype": "Data", "width": 130},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": _("Capacity"), "fieldname": "capacity", "fieldtype": "Int", "width": 90},
		{"label": _("Current Usage"), "fieldname": "current_usage", "fieldtype": "Int", "width": 100},
		{"label": _("Occupancy %"), "fieldname": "occupancy_percent", "fieldtype": "Percent", "width": 100},
		{"label": _("Nitrogen Level %"), "fieldname": "nitrogen_level", "fieldtype": "Percent", "width": 120},
		{"label": _("Alert"), "fieldname": "alert", "fieldtype": "Data", "width": 200},
	]


def get_data(filters):
	conditions = ["1=1"]
	values = {}
	if filters.get("status"):
		conditions.append("status = %(status)s")
		values["status"] = filters["status"]

	tanks = frappe.db.sql(
		f"""
		select name, location, status, capacity, current_usage, occupancy_percent,
			   nitrogen_level, occupancy_alert_threshold, nitrogen_threshold
		from `tabStorage Tank`
		where {' and '.join(conditions)}
		order by occupancy_percent desc
		""",
		values,
		as_dict=True,
	)

	for tank in tanks:
		reasons = []
		if (tank.occupancy_percent or 0) > (tank.occupancy_alert_threshold or 90):
			reasons.append(_("Occupancy high"))
		if tank.nitrogen_level is not None and tank.nitrogen_level < (tank.nitrogen_threshold or 20):
			reasons.append(_("Nitrogen low"))
		tank["alert"] = ", ".join(reasons)

	return tanks
