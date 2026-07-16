import frappe
from frappe.tests.utils import FrappeTestCase

from fertility_suite.tests.test_utils import create_test_ivf_cycle


class TestPregnancyFollowUp(FrappeTestCase):
	def test_live_birth_completes_cycle_and_marks_case_pregnant(self):
		cycle = create_test_ivf_cycle(status="Transfer")

		frappe.get_doc({
			"doctype": "Pregnancy Follow Up",
			"ivf_cycle": cycle.name,
			"beta_hcg": 250,
			"outcome": "Live Birth",
		}).insert(ignore_permissions=True)

		cycle.reload()
		self.assertEqual(cycle.status, "Completed")

		case = frappe.get_doc("Fertility Case", cycle.fertility_case)
		self.assertEqual(case.status, "Pregnant")

	def test_negative_outcome_completes_cycle_without_marking_pregnant(self):
		cycle = create_test_ivf_cycle(status="Transfer")

		frappe.get_doc({
			"doctype": "Pregnancy Follow Up",
			"ivf_cycle": cycle.name,
			"beta_hcg": 1,
			"outcome": "Negative",
		}).insert(ignore_permissions=True)

		cycle.reload()
		self.assertEqual(cycle.status, "Completed")

		case = frappe.get_doc("Fertility Case", cycle.fertility_case)
		self.assertNotEqual(case.status, "Pregnant")
