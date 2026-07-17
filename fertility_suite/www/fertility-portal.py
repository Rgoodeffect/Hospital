import frappe

no_cache = 1


def get_context(context):
	patient = None
	if frappe.session.user != "Guest":
		patient = frappe.db.get_value(
			"Patient", {"user_id": frappe.session.user}, ["name", "patient_name"], as_dict=True
		)

	context.patient = patient
	context.no_cache = 1
	return context
