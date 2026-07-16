import frappe
from frappe.tests.utils import FrappeTestCase

from fertility_suite.tests.test_utils import create_test_fertility_case, create_test_practitioner


class TestTreatmentPlan(FrappeTestCase):
	def test_create_treatment_plan(self):
		case = create_test_fertility_case()
		doctor = create_test_practitioner().name

		plan = frappe.get_doc({
			"doctype": "Treatment Plan",
			"fertility_case": case.name,
			"doctor": doctor,
			"protocol_type": "Antagonist Protocol",
		}).insert(ignore_permissions=True)

		self.assertEqual(plan.patient, case.patient)
		self.assertEqual(plan.status, "Draft")
