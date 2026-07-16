import frappe
from frappe import _
from frappe.model.document import Document

from fertility_suite.embryo_bank.doctype.gamete_donor.gamete_donor import recompute_screening_status


class DonorScreening(Document):
	def before_submit(self):
		if self.result == "Pending":
			frappe.throw(_("Cannot submit a Donor Screening while its result is still Pending"))

	def on_submit(self):
		recompute_screening_status(self.donor)
		if self.result == "Failed":
			from fertility_suite.notification_engine.notification_engine import notify

			notify(
				"Donor Screening Failed",
				{
					"donor": self.donor,
					"screening_type": self.screening_type,
					"reference_doctype": "Donor Screening",
					"reference_name": self.name,
				},
				roles=["Embryologist", "Clinic Manager"],
			)

	def on_cancel(self):
		recompute_screening_status(self.donor)
