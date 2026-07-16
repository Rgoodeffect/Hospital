import frappe
from frappe.tests.utils import FrappeTestCase

from fertility_suite.storage_tank_management.doctype.storage_tank.storage_tank import (
	recompute_tank_usage,
)


class TestStorageTank(FrappeTestCase):
	def test_occupancy_percent_is_computed(self):
		tank = frappe.get_doc({
			"doctype": "Storage Tank",
			"tank_id": f"TANK-{frappe.generate_hash(length=6)}",
			"capacity": 10,
			"nitrogen_level": 80,
		}).insert(ignore_permissions=True)

		updated = recompute_tank_usage(tank.name)
		self.assertEqual(updated.current_usage, 0)
		self.assertEqual(updated.occupancy_percent, 0)
