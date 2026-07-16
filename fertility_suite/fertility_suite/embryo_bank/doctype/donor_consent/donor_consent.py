import frappe
from frappe.model.document import Document

from fertility_suite.embryo_bank.doctype.gamete_donor.gamete_donor import recompute_consent_status


class DonorConsent(Document):
	def on_submit(self):
		if self.consent_type == "Withdrawal of Consent":
			_withdraw_donor(self)

		recompute_consent_status(self.donor)

	def on_cancel(self):
		recompute_consent_status(self.donor)


def _withdraw_donor(doc):
	other_active = frappe.get_all(
		"Donor Consent",
		filters={"donor": doc.donor, "is_active": 1, "name": ["!=", doc.name]},
		pluck="name",
	)
	for name in other_active:
		frappe.db.set_value("Donor Consent", name, "is_active", 0)

	frappe.db.set_value("Gamete Donor", doc.donor, "status", "Withdrawn")
