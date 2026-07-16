import frappe
from frappe.model.document import Document

from fertility_suite.notification_engine.notification_engine import notify


class StorageTank(Document):
	def validate(self):
		validate_tank(self)

	def on_update(self):
		check_alerts(self)


def validate_tank(doc, method=None):
	if doc.capacity and doc.capacity < 0:
		frappe.throw(frappe._("Capacity cannot be negative"))


def recompute_tank_usage(tank_name, save=True):
	usage = frappe.db.count(
		"Embryo Inventory",
		{"tank": tank_name, "status": ["in", ["Frozen", "Stored"]]},
	)
	usage += frappe.db.count(
		"Donor Bank Unit",
		{"tank": tank_name, "status": ["in", ["Available", "Reserved", "Allocated"]]},
	)
	tank = frappe.get_doc("Storage Tank", tank_name)
	occupancy = (usage / tank.capacity * 100) if tank.capacity else 0

	if save:
		tank.db_set("current_usage", usage, update_modified=False)
		tank.db_set("occupancy_percent", occupancy, update_modified=False)

	tank.current_usage = usage
	tank.occupancy_percent = occupancy
	return tank


def check_alerts(doc, method=None):
	"""Raise a Storage Tank Alert notification when occupancy or nitrogen
	level cross their configured thresholds."""
	occupancy_threshold = doc.occupancy_alert_threshold or 90
	nitrogen_threshold = doc.nitrogen_threshold or 20

	reasons = []
	if (doc.occupancy_percent or 0) > occupancy_threshold:
		reasons.append(
			frappe._("Occupancy at {0}% exceeds threshold of {1}%").format(
				round(doc.occupancy_percent, 1), occupancy_threshold
			)
		)

	if doc.nitrogen_level is not None and doc.nitrogen_level < nitrogen_threshold:
		reasons.append(
			frappe._("Nitrogen level at {0}% is below threshold of {1}%").format(
				doc.nitrogen_level, nitrogen_threshold
			)
		)

	if not reasons:
		return

	notify(
		"Storage Tank Alert",
		{
			"tank_id": doc.name,
			"alert_reason": "; ".join(reasons),
			"reference_doctype": "Storage Tank",
			"reference_name": doc.name,
		},
		roles=["Embryologist", "Clinic Manager"],
	)


def check_all_tank_alerts():
	"""Hourly cron entry point: re-evaluate every active tank's thresholds."""
	for tank_name in frappe.get_all("Storage Tank", filters={"status": "Active"}, pluck="name"):
		tank = recompute_tank_usage(tank_name)
		check_alerts(tank)
