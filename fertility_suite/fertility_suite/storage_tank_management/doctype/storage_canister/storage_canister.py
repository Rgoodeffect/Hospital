import frappe
from frappe.model.document import Document


class StorageCanister(Document):
	def validate(self):
		recompute_canister_usage(self.name, save=False, doc=self)


def recompute_canister_usage(canister_name, save=True, doc=None):
	usage = frappe.db.count(
		"Embryo Inventory",
		{"canister": canister_name, "status": ["in", ["Frozen", "Stored"]]},
	)

	if doc is None:
		doc = frappe.get_doc("Storage Canister", canister_name)

	doc.current_usage = usage
	if save:
		doc.db_set("current_usage", usage, update_modified=False)
	return usage
