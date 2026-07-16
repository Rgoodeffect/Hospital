import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"label": _("Embryologist"), "fieldname": "embryologist", "fieldtype": "Link", "options": "User", "width": 160},
		{"label": _("Records"), "fieldname": "total_records", "fieldtype": "Int", "width": 90},
		{"label": _("Fertilized Oocytes"), "fieldname": "fertilized", "fieldtype": "Int", "width": 130},
		{"label": _("Blastocysts"), "fieldname": "blastocysts", "fieldtype": "Int", "width": 100},
		{"label": _("Fertilization Rate %"), "fieldname": "fertilization_rate", "fieldtype": "Percent", "width": 140},
		{"label": _("Blastocyst Rate %"), "fieldname": "blastocyst_rate", "fieldtype": "Percent", "width": 130},
	]


def get_data(filters):
	conditions = ["1=1"]
	values = {}
	if filters.get("embryologist"):
		conditions.append("er.embryologist = %(embryologist)s")
		values["embryologist"] = filters["embryologist"]

	rows = frappe.db.sql(
		f"""
		select er.embryologist as embryologist,
			   count(er.name) as total_records,
			   sum(er.fertilized_oocytes) as fertilized,
			   sum(er.blastocysts) as blastocysts,
			   sum(eg.mature_oocytes) as mature
		from `tabEmbryology Record` er
		left join `tabEgg Retrieval` eg on eg.name = er.egg_retrieval
		where {' and '.join(conditions)}
		group by er.embryologist
		order by total_records desc
		""",
		values,
		as_dict=True,
	)

	for row in rows:
		row["fertilization_rate"] = round(row["fertilized"] / row["mature"] * 100, 2) if row["mature"] else 0
		row["blastocyst_rate"] = round(row["blastocysts"] / row["fertilized"] * 100, 2) if row["fertilized"] else 0
		row.pop("mature", None)

	return rows
