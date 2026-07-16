import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"label": _("Doctor"), "fieldname": "doctor", "fieldtype": "Link", "options": "Healthcare Practitioner", "width": 160},
		{"label": _("Total Cases"), "fieldname": "total_cases", "fieldtype": "Int", "width": 100},
		{"label": _("IVF Cycles"), "fieldname": "total_cycles", "fieldtype": "Int", "width": 100},
		{"label": _("Embryo Transfers"), "fieldname": "total_transfers", "fieldtype": "Int", "width": 120},
		{"label": _("Pregnancies"), "fieldname": "total_pregnancies", "fieldtype": "Int", "width": 100},
		{"label": _("Pregnancy Rate %"), "fieldname": "pregnancy_rate", "fieldtype": "Percent", "width": 120},
	]


def get_data(filters):
	conditions = ["1=1"]
	values = {}
	if filters.get("doctor"):
		conditions.append("fc.doctor = %(doctor)s")
		values["doctor"] = filters["doctor"]

	rows = frappe.db.sql(
		f"""
		select fc.doctor as doctor,
			   count(distinct fc.name) as total_cases,
			   count(distinct ic.name) as total_cycles,
			   count(distinct et.name) as total_transfers,
			   count(distinct case when pfu.outcome in ('Clinical Pregnancy', 'Ongoing Pregnancy', 'Live Birth')
					 then pfu.name end) as total_pregnancies
		from `tabFertility Case` fc
		left join `tabIVF Cycle` ic on ic.fertility_case = fc.name
		left join `tabEmbryo Transfer` et on et.ivf_cycle = ic.name and et.docstatus = 1
		left join `tabPregnancy Follow Up` pfu on pfu.ivf_cycle = ic.name
		where {' and '.join(conditions)}
		group by fc.doctor
		order by total_cases desc
		""",
		values,
		as_dict=True,
	)

	for row in rows:
		row["pregnancy_rate"] = (
			round(row["total_pregnancies"] / row["total_transfers"] * 100, 2) if row["total_transfers"] else 0
		)

	return rows
