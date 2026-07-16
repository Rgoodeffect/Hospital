import frappe
from frappe.tests.utils import FrappeTestCase

from fertility_suite.tests.test_utils import (
	create_test_donor_bank_unit,
	create_test_gamete_donor,
	create_test_storage_canister,
	create_test_storage_tank,
)


class TestDonorBankUnit(FrappeTestCase):
	def test_cannot_make_available_without_eligibility(self):
		donor = create_test_gamete_donor()
		with self.assertRaises(frappe.ValidationError):
			create_test_donor_bank_unit(donor=donor, status="Available")

	def test_eligible_donor_unit_can_be_made_available(self):
		donor = create_test_gamete_donor(screened=True, consented=True)
		unit = create_test_donor_bank_unit(donor=donor, status="Available")
		self.assertEqual(unit.status, "Available")

	def test_duplicate_storage_location_is_blocked(self):
		donor = create_test_gamete_donor(screened=True, consented=True)
		tank = create_test_storage_tank()
		canister = create_test_storage_canister(tank=tank)

		create_test_donor_bank_unit(
			donor=donor, status="Available", tank=tank.name, canister=canister.name,
			straw_number="1", position="A1",
		)

		with self.assertRaises(frappe.ValidationError):
			create_test_donor_bank_unit(
				donor=donor, status="Available", tank=tank.name, canister=canister.name,
				straw_number="1", position="A1",
			)

	def test_tank_usage_recomputed_on_save(self):
		donor = create_test_gamete_donor(screened=True, consented=True)
		tank = create_test_storage_tank(capacity=10)
		canister = create_test_storage_canister(tank=tank, capacity=5)

		create_test_donor_bank_unit(
			donor=donor, status="Available", tank=tank.name, canister=canister.name,
			straw_number="9", position="C9",
		)

		tank.reload()
		self.assertEqual(tank.current_usage, 1)
		self.assertEqual(tank.occupancy_percent, 10)
