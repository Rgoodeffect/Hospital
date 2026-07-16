import frappe
from frappe.tests.utils import FrappeTestCase

from fertility_suite.tests.test_utils import create_test_patient, create_test_practitioner


class TestFertilityCase(FrappeTestCase):
	def test_duplicate_active_case_is_blocked(self):
		patient = create_test_patient().name
		doctor = create_test_practitioner().name

		first_case = frappe.get_doc({
			"doctype": "Fertility Case",
			"patient": patient,
			"doctor": doctor,
			"status": "Draft",
		}).insert(ignore_permissions=True)

		second_case = frappe.get_doc({
			"doctype": "Fertility Case",
			"patient": patient,
			"doctor": doctor,
			"status": "Draft",
		})

		self.assertRaises(frappe.ValidationError, second_case.insert, ignore_permissions=True)

		first_case.status = "Closed"
		first_case.save(ignore_permissions=True)

		# now that the first case is closed, a new active case should be allowed
		second_case.insert(ignore_permissions=True)

	def test_closed_cases_do_not_block_new_case(self):
		patient = create_test_patient().name
		doctor = create_test_practitioner().name

		closed_case = frappe.get_doc({
			"doctype": "Fertility Case",
			"patient": patient,
			"doctor": doctor,
			"status": "Cancelled",
		}).insert(ignore_permissions=True)
		self.assertTrue(closed_case.name)

		new_case = frappe.get_doc({
			"doctype": "Fertility Case",
			"patient": patient,
			"doctor": doctor,
			"status": "Draft",
		}).insert(ignore_permissions=True)
		self.assertTrue(new_case.name)
