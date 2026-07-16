import frappe
from frappe.tests.utils import FrappeTestCase

from fertility_suite.insurance_management.doctype.pre_authorization.pre_authorization import approve
from fertility_suite.tests.test_utils import create_test_insurance_plan, create_test_patient


class TestPreAuthorization(FrappeTestCase):
	def test_approve_sets_status_and_amount(self):
		plan = create_test_insurance_plan()
		pre_auth = frappe.get_doc({
			"doctype": "Pre Authorization",
			"patient": create_test_patient().name,
			"insurance_plan": plan.name,
			"requested_amount": 5000,
		}).insert(ignore_permissions=True)

		approve(pre_auth.name, 4500)
		pre_auth.reload()

		self.assertEqual(pre_auth.status, "Approved")
		self.assertEqual(pre_auth.approved_amount, 4500)
