import frappe
from frappe import _
from frappe.model.document import Document


class EggRetrieval(Document):
	def validate(self):
		validate_retrieval(self)


def validate_retrieval(doc, method=None):
	mature = doc.mature_oocytes or 0
	retrieved = doc.retrieved_oocytes or 0

	if mature > retrieved:
		frappe.throw(
			_("Mature Oocytes ({0}) cannot exceed Retrieved Oocytes ({1})").format(mature, retrieved)
		)

	immature = doc.immature_oocytes or 0
	if mature + immature > retrieved:
		frappe.throw(
			_("Mature + Immature Oocytes ({0}) cannot exceed Retrieved Oocytes ({1})").format(
				mature + immature, retrieved
			)
		)
