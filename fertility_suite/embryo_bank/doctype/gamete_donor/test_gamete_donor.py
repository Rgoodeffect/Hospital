import frappe
from frappe.tests.utils import FrappeTestCase

from fertility_suite.tests.test_utils import create_test_gamete_donor


class TestGameteDonor(FrappeTestCase):
	def test_donor_code_is_auto_generated(self):
		donor = create_test_gamete_donor(donor_type="Egg")
		self.assertTrue(donor.donor_code)
		self.assertTrue(donor.donor_code.startswith("E-"))

	def test_donor_code_is_unique_per_type(self):
		first = create_test_gamete_donor(donor_type="Sperm")
		second = create_test_gamete_donor(donor_type="Sperm")
		self.assertNotEqual(first.donor_code, second.donor_code)
