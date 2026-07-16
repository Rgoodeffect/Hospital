import frappe
from frappe.tests.utils import FrappeTestCase

from fertility_suite.follicle_monitoring.doctype.monitoring_visit.monitoring_visit import (
	get_follicle_growth_timeline,
)
from fertility_suite.tests.test_utils import create_test_fertility_case


class TestMonitoringVisit(FrappeTestCase):
	def test_follicle_growth_timeline(self):
		case = create_test_fertility_case()
		cycle = frappe.get_doc({
			"doctype": "IVF Cycle",
			"fertility_case": case.name,
			"doctor": case.doctor,
		}).insert(ignore_permissions=True)

		frappe.get_doc({
			"doctype": "Monitoring Visit",
			"ivf_cycle": cycle.name,
			"visit_date": "2026-01-05",
			"endometrium_thickness": 8.2,
			"follicle_measurements": [
				{"ovary": "Right", "follicle_size": 12.0},
				{"ovary": "Right", "follicle_size": 14.5},
				{"ovary": "Left", "follicle_size": 11.0},
			],
		}).insert(ignore_permissions=True)

		timeline = get_follicle_growth_timeline(cycle.name)
		self.assertEqual(len(timeline), 1)
		self.assertEqual(timeline[0]["right_ovary_max"], 14.5)
		self.assertEqual(timeline[0]["left_ovary_max"], 11.0)
		self.assertEqual(timeline[0]["right_ovary_count"], 2)
