import frappe


def get_kpi_value(kpi_name: str, default=0):
	"""Jinja/template helper: fetch the latest snapshot value for a named KPI."""
	value = frappe.db.get_value(
		"KPI Snapshot",
		{"kpi_name": kpi_name},
		"kpi_value",
		order_by="snapshot_date desc",
	)
	return value if value is not None else default
