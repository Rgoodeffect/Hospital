import frappe
from frappe import _
from frappe.model.document import Document

TRANSFERABLE_STATUSES = ("Frozen", "Stored", "Reserved")


class EmbryoTransfer(Document):
	def validate(self):
		self._validate_no_duplicate_rows()

	def before_submit(self):
		before_submit(self)

	def on_submit(self):
		on_submit(self)

	def _validate_no_duplicate_rows(self):
		seen = set()
		for row in self.embryos:
			if row.embryo in seen:
				frappe.throw(_("Embryo {0} is listed more than once in this transfer").format(row.embryo))
			seen.add(row.embryo)


def before_submit(doc, method=None):
	for row in doc.embryos:
		status = frappe.db.get_value("Embryo Inventory", row.embryo, "status")
		if status not in TRANSFERABLE_STATUSES:
			frappe.throw(
				_("Embryo {0} cannot be transferred because its current status is '{1}'").format(
					row.embryo, status
				)
			)


def on_submit(doc, method=None):
	for row in doc.embryos:
		embryo = frappe.get_doc("Embryo Inventory", row.embryo)
		embryo.status = "Transferred"
		embryo.save(ignore_permissions=True)

	frappe.db.set_value("IVF Cycle", doc.ivf_cycle, "status", "Transfer")

	from fertility_suite.notification_engine.notification_engine import notify

	notify(
		"Embryo Transfer Scheduled",
		{
			"patient_name": doc.patient,
			"transfer_date": doc.transfer_date,
			"reference_doctype": "Embryo Transfer",
			"reference_name": doc.name,
		},
		roles=["Fertility Patient"],
	)
