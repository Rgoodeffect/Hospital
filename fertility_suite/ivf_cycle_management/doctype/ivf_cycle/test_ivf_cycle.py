import frappe
from frappe.tests.utils import FrappeTestCase

from fertility_suite.tests.test_utils import create_test_fertility_case


class TestIVFCycle(FrappeTestCase):
	def test_only_one_active_cycle_per_patient(self):
		case = create_test_fertility_case()

		first_cycle = frappe.get_doc({
			"doctype": "IVF Cycle",
			"fertility_case": case.name,
			"doctor": case.doctor,
			"status": "Planned",
		}).insert(ignore_permissions=True)

		second_cycle = frappe.get_doc({
			"doctype": "IVF Cycle",
			"fertility_case": case.name,
			"doctor": case.doctor,
			"status": "Planned",
		})
		self.assertRaises(frappe.ValidationError, second_cycle.insert, ignore_permissions=True)

		# IVF Cycle Workflow doesn't allow a direct Planned -> Completed
		# transition; jump the status directly the same way the app's own
		# business logic does elsewhere, bypassing the workflow's transition
		# graph for test setup.
		frappe.db.set_value("IVF Cycle", first_cycle.name, "status", "Completed")

		second_cycle.insert(ignore_permissions=True)
		self.assertTrue(second_cycle.name)
