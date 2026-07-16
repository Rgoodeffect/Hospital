import frappe
from frappe.tests.utils import FrappeTestCase

from fertility_suite.executive_dashboards.dashboard_engine import (
	generate_clinical_dashboard_snapshot,
	generate_weekly_executive_snapshot,
)
from fertility_suite.tests.test_utils import create_test_fertility_case


class TestDashboardEngine(FrappeTestCase):
	def test_clinical_snapshot_counts_active_case(self):
		create_test_fertility_case(status="Draft")

		name = generate_clinical_dashboard_snapshot()
		doc = frappe.get_doc("Clinical Dashboard Snapshot", name)
		self.assertGreaterEqual(doc.active_fertility_cases, 1)

	def test_weekly_executive_snapshot_is_created(self):
		name = generate_weekly_executive_snapshot()
		doc = frappe.get_doc("Executive Dashboard Snapshot", name)
		self.assertTrue(doc.name)
