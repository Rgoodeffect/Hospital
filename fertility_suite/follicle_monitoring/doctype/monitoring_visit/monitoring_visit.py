import frappe
from frappe.model.document import Document


class MonitoringVisit(Document):
	pass


@frappe.whitelist()
def get_follicle_growth_timeline(ivf_cycle: str):
	"""Return a per-visit timeline of follicle measurements for an IVF Cycle,
	suitable for plotting a growth chart on the client."""
	visits = frappe.get_all(
		"Monitoring Visit",
		filters={"ivf_cycle": ivf_cycle},
		fields=["name", "visit_date", "endometrium_thickness"],
		order_by="visit_date asc",
	)

	timeline = []
	for visit in visits:
		measurements = frappe.get_all(
			"Follicle Measurement",
			filters={"parent": visit.name, "parenttype": "Monitoring Visit"},
			fields=["ovary", "follicle_size"],
		)
		right = [m.follicle_size for m in measurements if m.ovary == "Right"]
		left = [m.follicle_size for m in measurements if m.ovary == "Left"]

		timeline.append({
			"visit_date": visit.visit_date,
			"endometrium_thickness": visit.endometrium_thickness,
			"right_ovary_max": max(right) if right else None,
			"left_ovary_max": max(left) if left else None,
			"right_ovary_count": len(right),
			"left_ovary_count": len(left),
		})

	return timeline
