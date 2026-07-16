import frappe
from frappe.tests.utils import FrappeTestCase

from fertility_suite.tests.test_utils import (
	create_test_donor_allocation,
	create_test_donor_bank_unit,
	create_test_gamete_donor,
	create_test_patient,
)


class TestDonorAllocation(FrappeTestCase):
	def test_cannot_allocate_unavailable_unit(self):
		donor = create_test_gamete_donor(screened=True, consented=True)
		unit = create_test_donor_bank_unit(donor=donor, status="Pending QC")
		patient = create_test_patient()

		allocation = create_test_donor_allocation(unit=unit, patient=patient, do_submit=False)
		self.assertRaises(frappe.ValidationError, allocation.submit)

	def test_submitting_allocation_marks_unit_allocated(self):
		donor = create_test_gamete_donor(screened=True, consented=True)
		unit = create_test_donor_bank_unit(donor=donor, status="Available")
		patient = create_test_patient()

		allocation = create_test_donor_allocation(unit=unit, patient=patient, status="Allocated")

		unit.reload()
		self.assertEqual(unit.status, "Allocated")
		self.assertEqual(allocation.docstatus, 1)

	def test_cancelling_allocation_frees_unit(self):
		donor = create_test_gamete_donor(screened=True, consented=True)
		unit = create_test_donor_bank_unit(donor=donor, status="Available")
		patient = create_test_patient()

		allocation = create_test_donor_allocation(unit=unit, patient=patient, status="Allocated")
		allocation.cancel()

		unit.reload()
		self.assertEqual(unit.status, "Available")

	def test_consent_must_be_confirmed(self):
		donor = create_test_gamete_donor(screened=True, consented=True)
		unit = create_test_donor_bank_unit(donor=donor, status="Available")
		patient = create_test_patient()

		with self.assertRaises(frappe.ValidationError):
			create_test_donor_allocation(unit=unit, patient=patient, consent_confirmed=0)
