import frappe
from frappe import _
from frappe.model.document import Document


class PreAuthorization(Document):
	def validate(self):
		if self.status == "Approved" and not self.approved_amount:
			frappe.throw(_("Approved Amount is required when status is Approved"))


@frappe.whitelist()
def approve(pre_authorization: str, approved_amount: float):
	doc = frappe.get_doc("Pre Authorization", pre_authorization)
	doc.approved_amount = approved_amount
	doc.status = "Approved"
	doc.save()
	return doc.name
