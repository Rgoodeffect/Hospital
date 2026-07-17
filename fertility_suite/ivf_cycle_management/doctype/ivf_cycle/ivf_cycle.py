import frappe
from frappe import _
from frappe.model.document import Document

ACTIVE_EXCLUDED_STATUSES = ("Completed", "Cancelled")


class IVFCycle(Document):
	def validate(self):
		validate_cycle(self)


def validate_cycle(doc, method=None):
	"""Enforce a single active IVF Cycle per patient."""
	if doc.status in ACTIVE_EXCLUDED_STATUSES:
		return

	duplicate = frappe.db.exists(
		"IVF Cycle",
		{
			"patient": doc.patient,
			"status": ["not in", ACTIVE_EXCLUDED_STATUSES],
			"name": ["!=", doc.name or ""],
		},
	)

	if duplicate:
		frappe.throw(
			_("Patient {0} already has an active IVF Cycle {1}").format(
				frappe.bold(doc.patient), frappe.bold(duplicate)
			)
		)


def get_permission_query_conditions(user):
	if not user:
		user = frappe.session.user

	roles = frappe.get_roles(user)
	if "Fertility Patient" not in roles or "System Manager" in roles:
		return ""

	patient = frappe.db.get_value("Patient", {"user_id": user}, "name")
	if not patient:
		return "1=0"

	return f"`tabIVF Cycle`.patient = {frappe.db.escape(patient)}"


def has_permission(doc, user):
	if not user:
		user = frappe.session.user

	roles = frappe.get_roles(user)
	if "Fertility Patient" not in roles or "System Manager" in roles:
		return True

	patient = frappe.db.get_value("Patient", {"user_id": user}, "name")
	return bool(patient) and doc.patient == patient
