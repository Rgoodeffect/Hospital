import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"label": _("Outcome"), "fieldname": "outcome", "fieldtype": "Data", "width": 150},
		{"label": _("Count"), "fieldname": "count", "fieldtype": "Int", "width": 100},
		{"label": _("Percent of Total"), "fieldname": "percent_of_total", "fieldtype": "Percent", "width": 130},
	]


def get_data(filters):
	conditions = ["outcome is not null and outcome != ''"]
	values = {}

	if filters.get("from_date"):
		conditions.append("follow_up_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]

	if filters.get("to_date"):
		conditions.append("follow_up_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]

	rows = frappe.db.sql(
		f"""
		select outcome, count(*) as count
		from `tabPregnancy Follow Up`
		where {' and '.join(conditions)}
		group by outcome
		order by count desc
		""",
		values,
		as_dict=True,
	)

	total = sum(row["count"] for row in rows) or 1
	for row in rows:
		row["percent_of_total"] = round(row["count"] / total * 100, 2)

	return rows
