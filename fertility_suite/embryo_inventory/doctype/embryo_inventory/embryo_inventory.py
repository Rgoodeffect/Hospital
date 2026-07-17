import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime

OCCUPYING_STATUSES = ("Frozen", "Stored", "Reserved")


class EmbryoInventory(Document):
	def validate(self):
		validate_inventory(self)
		self._record_status_transition()

	def on_update(self):
		recompute_storage_usage(self)

	def _record_status_transition(self):
		if self.is_new() or not self.has_value_changed("status"):
			return

		previous_status = self.get_doc_before_save().status if self.get_doc_before_save() else None
		self.append("status_history", {
			"previous_status": previous_status,
			"new_status": self.status,
			"changed_by": frappe.session.user,
			"changed_on": now_datetime(),
		})


def validate_inventory(doc, method=None):
	"""Prevent two embryos from occupying the same tank/canister/straw/position
	while both are physically in storage."""
	if doc.status not in OCCUPYING_STATUSES:
		return

	if not (doc.tank and doc.canister and doc.straw_number and doc.position):
		return

	duplicate = frappe.db.exists(
		"Embryo Inventory",
		{
			"tank": doc.tank,
			"canister": doc.canister,
			"straw_number": doc.straw_number,
			"position": doc.position,
			"status": ["in", OCCUPYING_STATUSES],
			"name": ["!=", doc.name or ""],
		},
	)

	if duplicate:
		frappe.throw(
			_("Storage location Tank {0} / Canister {1} / Straw {2} / Position {3} is already occupied by {4}").format(
				doc.tank, doc.canister, doc.straw_number, doc.position, duplicate
			)
		)


def recompute_storage_usage(doc, method=None):
	from fertility_suite.storage_tank_management.doctype.storage_tank.storage_tank import (
		recompute_tank_usage,
	)
	from fertility_suite.storage_tank_management.doctype.storage_canister.storage_canister import (
		recompute_canister_usage,
	)

	for tank_name in filter(None, {doc.tank}):
		recompute_tank_usage(tank_name)

	for canister_name in filter(None, {doc.canister}):
		recompute_canister_usage(canister_name)


def get_permission_query_conditions(user):
	if not user:
		user = frappe.session.user

	roles = frappe.get_roles(user)
	if "Fertility Patient" not in roles or "System Manager" in roles:
		return ""

	patient = frappe.db.get_value("Patient", {"user_id": user}, "name")
	if not patient:
		return "1=0"

	return f"`tabEmbryo Inventory`.patient = {frappe.db.escape(patient)}"


def has_permission(doc, user):
	if not user:
		user = frappe.session.user

	roles = frappe.get_roles(user)
	if "Fertility Patient" not in roles or "System Manager" in roles:
		return True

	patient = frappe.db.get_value("Patient", {"user_id": user}, "name")
	return bool(patient) and doc.patient == patient
