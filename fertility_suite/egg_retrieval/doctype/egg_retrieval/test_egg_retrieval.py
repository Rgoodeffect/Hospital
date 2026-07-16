import frappe
from frappe.tests.utils import FrappeTestCase

from fertility_suite.tests.test_utils import create_test_fertility_case


class TestEggRetrieval(FrappeTestCase):
	def setUp(self):
		case = create_test_fertility_case()
		self.cycle = frappe.get_doc({
			"doctype": "IVF Cycle",
			"fertility_case": case.name,
			"doctor": case.doctor,
		}).insert(ignore_permissions=True)

	def test_mature_cannot_exceed_retrieved(self):
		retrieval = frappe.get_doc({
			"doctype": "Egg Retrieval",
			"ivf_cycle": self.cycle.name,
			"doctor": self.cycle.doctor,
			"retrieved_oocytes": 5,
			"mature_oocytes": 8,
		})
		self.assertRaises(frappe.ValidationError, retrieval.insert, ignore_permissions=True)

	def test_valid_counts_are_accepted(self):
		retrieval = frappe.get_doc({
			"doctype": "Egg Retrieval",
			"ivf_cycle": self.cycle.name,
			"doctor": self.cycle.doctor,
			"retrieved_oocytes": 10,
			"mature_oocytes": 7,
			"immature_oocytes": 2,
		}).insert(ignore_permissions=True)
		self.assertTrue(retrieval.name)
