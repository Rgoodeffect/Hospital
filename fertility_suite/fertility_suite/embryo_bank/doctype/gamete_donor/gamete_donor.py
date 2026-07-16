import frappe
from frappe.model.document import Document

DONOR_TYPE_PREFIX = {"Egg": "E", "Sperm": "S", "Embryo": "M"}


class GameteDonor(Document):
	def before_insert(self):
		if not self.donor_code:
			self.donor_code = generate_donor_code(self.donor_type)


def generate_donor_code(donor_type):
	prefix = DONOR_TYPE_PREFIX.get(donor_type, "D")
	while True:
		code = f"{prefix}-{frappe.generate_hash(length=8).upper()}"
		if not frappe.db.exists("Gamete Donor", {"donor_code": code}):
			return code


def recompute_screening_status(donor_name):
	"""Re-derive Gamete Donor.screening_status/last_screening_date from the
	most recent submitted Donor Screening. Called on submit/cancel of a
	Donor Screening so the donor record always reflects its latest state."""
	latest = frappe.db.get_value(
		"Donor Screening",
		{"donor": donor_name, "docstatus": 1},
		["result", "screening_date"],
		order_by="screening_date desc, creation desc",
		as_dict=True,
	)

	if not latest:
		frappe.db.set_value("Gamete Donor", donor_name, {
			"screening_status": "Not Screened",
			"last_screening_date": None,
		})
		return

	updates = {"screening_status": latest.result, "last_screening_date": latest.screening_date}
	if latest.result == "Failed":
		updates["status"] = "Disqualified"

	frappe.db.set_value("Gamete Donor", donor_name, updates)


def recompute_consent_status(donor_name):
	"""Re-derive Gamete Donor.consent_on_file from active, submitted,
	non-expired Donor Consent records that are not a withdrawal."""
	today = frappe.utils.getdate()
	candidates = frappe.get_all(
		"Donor Consent",
		filters={
			"donor": donor_name,
			"docstatus": 1,
			"is_active": 1,
			"consent_type": ["!=", "Withdrawal of Consent"],
		},
		pluck="expiry_date",
	)
	has_active_consent = any(
		not expiry_date or frappe.utils.getdate(expiry_date) >= today for expiry_date in candidates
	)

	frappe.db.set_value("Gamete Donor", donor_name, "consent_on_file", 1 if has_active_consent else 0)
