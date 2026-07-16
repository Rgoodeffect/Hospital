import frappe
from frappe.tests.utils import FrappeTestCase

from fertility_suite.tests.test_utils import create_test_embryo, create_test_embryology_record


class TestEmbryoTransfer(FrappeTestCase):
	def _make_transfer(self, cycle, embryo):
		return frappe.get_doc({
			"doctype": "Embryo Transfer",
			"ivf_cycle": cycle,
			"doctor": frappe.db.get_value("IVF Cycle", cycle, "doctor"),
			"embryos": [{"embryo": embryo}],
		})

	def test_transferring_same_embryo_twice_is_blocked(self):
		record = create_test_embryology_record()
		embryo = create_test_embryo(record, status="Stored")
		cycle = record.ivf_cycle

		first_transfer = self._make_transfer(cycle, embryo.name)
		first_transfer.insert(ignore_permissions=True)
		first_transfer.submit()

		embryo.reload()
		self.assertEqual(embryo.status, "Transferred")

		second_transfer = self._make_transfer(cycle, embryo.name)
		second_transfer.insert(ignore_permissions=True)
		self.assertRaises(frappe.ValidationError, second_transfer.submit)

	def test_duplicate_embryo_within_same_transfer_is_blocked(self):
		record = create_test_embryology_record()
		embryo = create_test_embryo(record, status="Stored")
		cycle = record.ivf_cycle

		transfer = frappe.get_doc({
			"doctype": "Embryo Transfer",
			"ivf_cycle": cycle,
			"doctor": frappe.db.get_value("IVF Cycle", cycle, "doctor"),
			"embryos": [{"embryo": embryo.name}, {"embryo": embryo.name}],
		})
		self.assertRaises(frappe.ValidationError, transfer.insert, ignore_permissions=True)
