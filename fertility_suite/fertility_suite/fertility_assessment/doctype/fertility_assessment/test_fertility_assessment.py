import frappe
from frappe.tests.utils import FrappeTestCase

from fertility_suite.tests.test_utils import create_test_fertility_case


class TestFertilityAssessment(FrappeTestCase):
	def test_patient_is_fetched_from_case(self):
		case = create_test_fertility_case()

		assessment = frappe.get_doc({
			"doctype": "Fertility Assessment",
			"fertility_case": case.name,
			"amh": 2.5,
			"fsh": 6.1,
			"afc_right": 8,
			"afc_left": 7,
		}).insert(ignore_permissions=True)

		self.assertEqual(assessment.patient, case.patient)
