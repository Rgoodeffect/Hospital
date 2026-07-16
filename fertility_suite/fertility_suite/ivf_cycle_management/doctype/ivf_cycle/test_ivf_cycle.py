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

		first_cycle.status = "Completed"
		first_cycle.save(ignore_permissions=True)

		second_cycle.insert(ignore_permissions=True)
		self.assertTrue(second_cycle.name)
