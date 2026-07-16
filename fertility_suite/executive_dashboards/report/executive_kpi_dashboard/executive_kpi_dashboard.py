import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"label": _("KPI"), "fieldname": "kpi_name", "fieldtype": "Data", "width": 200},
		{"label": _("Dimension"), "fieldname": "dimension", "fieldtype": "Data", "width": 150},
		{"label": _("Latest Value"), "fieldname": "kpi_value", "fieldtype": "Float", "width": 120},
		{"label": _("Snapshot Date"), "fieldname": "snapshot_date", "fieldtype": "Date", "width": 120},
	]


def get_data(filters):
	conditions = ["1=1"]
	values = {}
	if filters.get("kpi_name"):
		conditions.append("kpi_name = %(kpi_name)s")
		values["kpi_name"] = filters["kpi_name"]

	return frappe.db.sql(
		f"""
		select k1.kpi_name, k1.dimension, k1.kpi_value, k1.snapshot_date
		from `tabKPI Snapshot` k1
		inner join (
			select kpi_name, coalesce(dimension, '') as dimension, max(snapshot_date) as latest_date
			from `tabKPI Snapshot`
			group by kpi_name, coalesce(dimension, '')
		) latest
			on latest.kpi_name = k1.kpi_name
			and coalesce(latest.dimension, '') = coalesce(k1.dimension, '')
			and latest.latest_date = k1.snapshot_date
		where {' and '.join(conditions)}
		order by k1.kpi_name, k1.dimension
		""",
		values,
		as_dict=True,
	)
