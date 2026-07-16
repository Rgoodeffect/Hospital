import frappe
from frappe.tests.utils import FrappeTestCase

from fertility_suite.tests.test_utils import create_test_insurance_plan, create_test_patient


class TestInsuranceClaim(FrappeTestCase):
	def _make_claim(self, plan, total_amount):
		return frappe.get_doc({
			"doctype": "Insurance Claim",
			"patient": create_test_patient().name,
			"insurance_plan": plan.name,
			"total_amount": total_amount,
		}).insert(ignore_permissions=True)

	def test_cash_billing(self):
		plan = create_test_insurance_plan(billing_type="Cash")
		claim = self._make_claim(plan, 1000)

		self.assertEqual(claim.insurance_amount, 0)
		self.assertEqual(claim.patient_payable_amount, 1000)

	def test_insurance_billing(self):
		plan = create_test_insurance_plan(billing_type="Insurance", coverage_percent=80)
		claim = self._make_claim(plan, 1000)

		self.assertEqual(claim.insurance_amount, 800)
		self.assertEqual(claim.patient_payable_amount, 200)

	def test_insurance_billing_capped_at_plan_max(self):
		plan = create_test_insurance_plan(billing_type="Insurance", coverage_percent=80, max_coverage_amount=500)
		claim = self._make_claim(plan, 1000)

		self.assertEqual(claim.insurance_amount, 500)
		self.assertEqual(claim.patient_payable_amount, 500)

	def test_co_payment_billing(self):
		plan = create_test_insurance_plan(billing_type="Co-Payment", co_payment_percent=25)
		claim = self._make_claim(plan, 1000)

		self.assertEqual(claim.co_payment_amount, 250)
		self.assertEqual(claim.insurance_amount, 750)
		self.assertEqual(claim.patient_payable_amount, 250)

	def test_mixed_billing(self):
		plan = create_test_insurance_plan(
			billing_type="Mixed Billing", coverage_percent=60, co_payment_percent=50
		)
		claim = self._make_claim(plan, 1000)

		# insurance covers 60% = 600; remaining 400 is co-paid at 50% = 200
		self.assertEqual(claim.insurance_amount, 600)
		self.assertEqual(claim.co_payment_amount, 200)
		self.assertEqual(claim.patient_payable_amount, 400)
