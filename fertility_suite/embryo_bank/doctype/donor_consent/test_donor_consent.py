import frappe
from frappe.tests.utils import FrappeTestCase

from fertility_suite.tests.test_utils import create_test_donor_consent, create_test_gamete_donor


class TestDonorConsent(FrappeTestCase):
	def test_active_consent_marks_donor_consent_on_file(self):
		donor = create_test_gamete_donor()
		create_test_donor_consent(donor=donor, consent_type="Donation for Treatment")

		donor.reload()
		self.assertTrue(donor.consent_on_file)

	def test_withdrawal_deactivates_prior_consent_and_donor(self):
		donor = create_test_gamete_donor()
		create_test_donor_consent(donor=donor, consent_type="Donation for Treatment")
		create_test_donor_consent(donor=donor, consent_type="Withdrawal of Consent")

		donor.reload()
		self.assertFalse(donor.consent_on_file)
		self.assertEqual(donor.status, "Withdrawn")
