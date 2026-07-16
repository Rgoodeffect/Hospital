import frappe
from frappe import _
from frappe.model.document import Document


class DonorAllocation(Document):
	def validate(self):
		if not self.consent_confirmed:
			frappe.throw(_("Recipient consent must be confirmed before allocating donor material"))

	def before_submit(self):
		unit_status = frappe.db.get_value("Donor Bank Unit", self.donor_bank_unit, "status")
		if unit_status != "Available":
			frappe.throw(
				_("Donor Bank Unit {0} is not Available for allocation (current status: {1})").format(
					self.donor_bank_unit, unit_status
				)
			)

	def on_submit(self):
		frappe.db.set_value("Donor Bank Unit", self.donor_bank_unit, "status", self.status)

		from fertility_suite.notification_engine.notification_engine import notify

		notify(
			"Donor Unit Allocated",
			{
				"donor_bank_unit": self.donor_bank_unit,
				"recipient_patient": self.recipient_patient,
				"reference_doctype": "Donor Allocation",
				"reference_name": self.name,
			},
			roles=["Embryologist", "Clinic Manager"],
		)

	def on_cancel(self):
		unit_status = frappe.db.get_value("Donor Bank Unit", self.donor_bank_unit, "status")
		if unit_status == self.status:
			frappe.db.set_value("Donor Bank Unit", self.donor_bank_unit, "status", "Available")
