import frappe
from frappe.tests.utils import FrappeTestCase

from fertility_suite.tests.test_utils import (
	create_test_embryo,
	create_test_embryology_record,
	create_test_storage_canister,
	create_test_storage_tank,
)


class TestEmbryoInventory(FrappeTestCase):
	def test_duplicate_storage_location_is_blocked(self):
		record = create_test_embryology_record()
		tank = create_test_storage_tank()
		canister = create_test_storage_canister(tank=tank)

		create_test_embryo(record, tank=tank.name, canister=canister.name, straw_number="1", position="A1")

		second_record = create_test_embryology_record()
		with self.assertRaises(frappe.ValidationError):
			create_test_embryo(second_record, tank=tank.name, canister=canister.name, straw_number="1", position="A1")

	def test_discarding_frees_storage_location(self):
		record = create_test_embryology_record()
		tank = create_test_storage_tank()
		canister = create_test_storage_canister(tank=tank)

		embryo = create_test_embryo(record, tank=tank.name, canister=canister.name, straw_number="2", position="B2")
		embryo.status = "Discarded"
		embryo.save(ignore_permissions=True)

		second_record = create_test_embryology_record()
		new_embryo = create_test_embryo(
			second_record, tank=tank.name, canister=canister.name, straw_number="2", position="B2"
		)
		self.assertTrue(new_embryo.name)

	def test_status_history_is_recorded(self):
		embryo = create_test_embryo(status="Created")
		embryo.status = "Frozen"
		embryo.save(ignore_permissions=True)

		self.assertEqual(len(embryo.status_history), 1)
		self.assertEqual(embryo.status_history[0].previous_status, "Created")
		self.assertEqual(embryo.status_history[0].new_status, "Frozen")

	def test_tank_usage_recomputed_on_save(self):
		tank = create_test_storage_tank(capacity=10)
		canister = create_test_storage_canister(tank=tank, capacity=5)
		record = create_test_embryology_record()

		create_test_embryo(record, tank=tank.name, canister=canister.name, straw_number="9", position="C9")

		tank.reload()
		self.assertEqual(tank.current_usage, 1)
		self.assertEqual(tank.occupancy_percent, 10)
