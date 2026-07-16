import frappe

FERTILITY_ROLES = [
	"Fertility Doctor",
	"Embryologist",
	"IVF Coordinator",
	"Fertility Nurse",
	"Insurance Officer",
	"Clinic Manager",
	"Fertility Patient",
]


def after_install():
	create_fertility_roles()
	create_default_notification_templates()
	frappe.db.commit()


def before_tests():
	frappe.clear_cache()
	create_fertility_roles()
	create_default_notification_templates()

	if not frappe.db.get_single_value("System Settings", "country"):
		frappe.db.set_single_value("System Settings", "country", "United Arab Emirates")

	frappe.db.commit()


def create_fertility_roles():
	for role_name in FERTILITY_ROLES:
		if not frappe.db.exists("Role", role_name):
			frappe.get_doc({
				"doctype": "Role",
				"role_name": role_name,
				"desk_access": 0 if role_name == "Fertility Patient" else 1,
			}).insert(ignore_permissions=True)


def create_default_notification_templates():
	from fertility_suite.notification_engine.notification_engine import DEFAULT_TEMPLATES

	for template in DEFAULT_TEMPLATES:
		if not frappe.db.exists("Notification Template", template["name"]):
			frappe.get_doc({
				"doctype": "Notification Template",
				**template,
			}).insert(ignore_permissions=True)
