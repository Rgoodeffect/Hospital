import frappe
from frappe.tests.utils import FrappeTestCase

from fertility_suite.api import get_fertility_cases
from fertility_suite.tests.test_utils import create_test_fertility_case, create_test_patient


class TestFertilitySuiteAPI(FrappeTestCase):
	def test_staff_can_query_any_patient(self):
		case = create_test_fertility_case()
		results = get_fertility_cases(patient=case.patient)
		self.assertTrue(any(row.name == case.name for row in results))

	def test_portal_patient_is_pinned_to_own_record(self):
		patient = create_test_patient()
		user = frappe.get_doc({
			"doctype": "User",
			"email": f"{frappe.generate_hash(length=6)}@example.com",
			"first_name": "Portal Patient",
			"send_welcome_email": 0,
		}).insert(ignore_permissions=True)
		user.add_roles("Fertility Patient")
		frappe.db.set_value("Patient", patient.name, "user_id", user.name)

		other_case = create_test_fertility_case()

		frappe.set_user(user.name)
		try:
			results = get_fertility_cases(patient=other_case.patient)
			self.assertFalse(any(row.name == other_case.name for row in results))
		finally:
			frappe.set_user("Administrator")
