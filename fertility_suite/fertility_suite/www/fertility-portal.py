import frappe

no_cache = 1


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.throw("Please login to access the Fertility Portal", frappe.PermissionError)

	patient = frappe.db.get_value("Patient", {"user_id": frappe.session.user}, ["name", "patient_name"], as_dict=True)
	if not patient:
		frappe.throw("No Patient record is linked to your account", frappe.PermissionError)

	context.patient = patient
	context.no_cache = 1
	return context
