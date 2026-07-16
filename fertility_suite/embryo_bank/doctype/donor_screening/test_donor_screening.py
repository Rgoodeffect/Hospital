import frappe
from frappe.tests.utils import FrappeTestCase

from fertility_suite.tests.test_utils import create_test_donor_screening, create_test_gamete_donor


class TestDonorScreening(FrappeTestCase):
	def test_pending_result_cannot_be_submitted(self):
		donor = create_test_gamete_donor()
		screening = create_test_donor_screening(donor=donor, result="Pending", do_submit=False)
		self.assertRaises(frappe.ValidationError, screening.submit)

	def test_passed_result_updates_donor(self):
		donor = create_test_gamete_donor()
		create_test_donor_screening(donor=donor, result="Passed")

		donor.reload()
		self.assertEqual(donor.screening_status, "Passed")
		self.assertTrue(donor.last_screening_date)

	def test_failed_result_disqualifies_donor(self):
		donor = create_test_gamete_donor()
		create_test_donor_screening(donor=donor, result="Failed")

		donor.reload()
		self.assertEqual(donor.screening_status, "Failed")
		self.assertEqual(donor.status, "Disqualified")
