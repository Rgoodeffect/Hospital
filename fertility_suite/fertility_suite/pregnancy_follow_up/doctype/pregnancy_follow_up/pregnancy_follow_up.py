import frappe
from frappe.model.document import Document

CYCLE_COMPLETING_OUTCOMES = ("Negative", "Live Birth", "Miscarriage")
PREGNANCY_CONFIRMING_OUTCOMES = ("Clinical Pregnancy", "Ongoing Pregnancy", "Live Birth")


class PregnancyFollowUp(Document):
	def on_update(self):
		on_update(self)


def on_update(doc, method=None):
	if not doc.outcome or not doc.ivf_cycle:
		return

	if doc.outcome in CYCLE_COMPLETING_OUTCOMES:
		frappe.db.set_value("IVF Cycle", doc.ivf_cycle, "status", "Completed")

	fertility_case = frappe.db.get_value("IVF Cycle", doc.ivf_cycle, "fertility_case")
	if not fertility_case:
		return

	if doc.outcome in PREGNANCY_CONFIRMING_OUTCOMES:
		frappe.db.set_value("Fertility Case", fertility_case, "status", "Pregnant")
