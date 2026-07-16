import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from fertility_suite.analytics_and_kpi_engine.kpi_engine import (
	blastocyst_rate,
	claim_approval_rate,
	fertilization_rate,
)
from fertility_suite.tests.test_utils import create_test_embryology_record, create_test_insurance_plan, create_test_patient


class TestKPIEngine(FrappeTestCase):
	def test_fertilization_and_blastocyst_rate(self):
		period_start, period_end = add_days(today(), -1), today()
		create_test_embryology_record(fertilized_oocytes=8, day5_embryos=4, day6_embryos=1, blastocysts=4)

		self.assertGreater(fertilization_rate(period_start, period_end), 0)
		self.assertGreater(blastocyst_rate(period_start, period_end), 0)

	def test_claim_approval_rate(self):
		period_start, period_end = add_days(today(), -1), today()
		plan = create_test_insurance_plan(billing_type="Insurance", coverage_percent=80)
		patient = create_test_patient().name

		frappe.get_doc({
			"doctype": "Insurance Claim",
			"patient": patient,
			"insurance_plan": plan.name,
			"total_amount": 1000,
			"status": "Approved",
		}).insert(ignore_permissions=True)

		frappe.get_doc({
			"doctype": "Insurance Claim",
			"patient": patient,
			"insurance_plan": plan.name,
			"total_amount": 500,
			"status": "Rejected",
		}).insert(ignore_permissions=True)

		rate = claim_approval_rate(period_start, period_end)
		self.assertEqual(rate, 50.0)
