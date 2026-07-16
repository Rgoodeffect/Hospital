import frappe
from frappe.tests.utils import FrappeTestCase

from fertility_suite.tests.test_utils import create_test_fertility_case


class TestEmbryologyRecord(FrappeTestCase):
	def setUp(self):
		case = create_test_fertility_case()
		self.cycle = frappe.get_doc({
			"doctype": "IVF Cycle",
			"fertility_case": case.name,
			"doctor": case.doctor,
		}).insert(ignore_permissions=True)
		self.retrieval = frappe.get_doc({
			"doctype": "Egg Retrieval",
			"ivf_cycle": self.cycle.name,
			"doctor": self.cycle.doctor,
			"retrieved_oocytes": 10,
			"mature_oocytes": 8,
		}).insert(ignore_permissions=True)

	def test_fertilized_cannot_exceed_mature(self):
		record = frappe.get_doc({
			"doctype": "Embryology Record",
			"ivf_cycle": self.cycle.name,
			"egg_retrieval": self.retrieval.name,
			"embryologist": "Administrator",
			"fertilization_method": "ICSI",
			"fertilized_oocytes": 9,
		})
		self.assertRaises(frappe.ValidationError, record.insert, ignore_permissions=True)

	def test_blastocysts_cannot_exceed_day5_and_day6(self):
		record = frappe.get_doc({
			"doctype": "Embryology Record",
			"ivf_cycle": self.cycle.name,
			"egg_retrieval": self.retrieval.name,
			"embryologist": "Administrator",
			"fertilization_method": "ICSI",
			"fertilized_oocytes": 6,
			"day5_embryos": 2,
			"day6_embryos": 1,
			"blastocysts": 5,
		})
		self.assertRaises(frappe.ValidationError, record.insert, ignore_permissions=True)

	def test_valid_record_is_accepted(self):
		record = frappe.get_doc({
			"doctype": "Embryology Record",
			"ivf_cycle": self.cycle.name,
			"egg_retrieval": self.retrieval.name,
			"embryologist": "Administrator",
			"fertilization_method": "ICSI",
			"fertilized_oocytes": 6,
			"day3_embryos": 5,
			"day5_embryos": 3,
			"day6_embryos": 1,
			"blastocysts": 3,
		}).insert(ignore_permissions=True)
		self.assertTrue(record.name)
