import frappe
from frappe import _
from frappe.model.document import Document

CLOSED_STATUSES = ("Closed", "Cancelled")


class FertilityCase(Document):
	def validate(self):
		validate_case(self)


def validate_case(doc, method=None):
	"""Prevent a patient from having more than one active Fertility Case at a time."""
	if doc.status in CLOSED_STATUSES:
		return

	duplicate = frappe.db.exists(
		"Fertility Case",
		{
			"patient": doc.patient,
			"status": ["not in", CLOSED_STATUSES],
			"name": ["!=", doc.name or ""],
		},
	)

	if duplicate:
		frappe.throw(
			_("Patient {0} already has an active Fertility Case {1}").format(
				frappe.bold(doc.patient), frappe.bold(duplicate)
			)
		)


def get_permission_query_conditions(user):
	if not user:
		user = frappe.session.user

	if "Fertility Patient" not in frappe.get_roles(user):
		return ""

	patient = frappe.db.get_value("Patient", {"user_id": user}, "name")
	if not patient:
		return "1=0"

	return f"`tabFertility Case`.patient = {frappe.db.escape(patient)}"


def has_permission(doc, user):
	if not user:
		user = frappe.session.user

	if "Fertility Patient" not in frappe.get_roles(user):
		return True

	patient = frappe.db.get_value("Patient", {"user_id": user}, "name")
	return bool(patient) and doc.patient == patient
