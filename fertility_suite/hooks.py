from . import __version__ as app_version

app_name = "fertility_suite"
app_title = "Fertility Suite"
app_publisher = "RGoodEffect"
app_description = (
	"Fertility, IVF, Embryology and Embryo Bank Management Suite for ERPNext Healthcare"
)
app_email = "support@rgoodeffect.example"
app_license = "MIT"
app_icon = "octicon octicon-heart"
app_color = "#e83e8c"

required_apps = ["frappe", "erpnext", "healthcare"]

# Includes in <head>
# ------------------
app_include_css = [
	"/assets/fertility_suite/css/fertility_suite.css",
	"/assets/fertility_suite/css/fertility_theme.css",
]
app_include_js = [
	"/assets/fertility_suite/js/fertility_suite.js",
	"/assets/fertility_suite/js/fertility_ui.js",
	"/assets/fertility_suite/js/fertility_sidebar.js",
	"/assets/fertility_suite/js/fertility_dashboard.js",
]

# include js, css files in header of web template
web_include_css = [
	"/assets/fertility_suite/css/fertility_suite.css",
	"/assets/fertility_suite/css/fertility_theme.css",
]

# Doctype Class Overrides not required - we do not modify Healthcare/ERPNext core doctypes.

doctype_js = {
	"Patient": "public/js/patient_extensions.js",
}

# Document Events
# ---------------
# All Fertility Suite DocTypes own their controller class, so their
# validate/on_update/before_submit/on_submit logic lives directly on the
# Document subclass in each doctype's .py file rather than here. doc_events
# is reserved for hooking into ERPNext/Healthcare core doctypes we do not
# own the controller of.
doc_events = {}

# Scheduled Tasks
# ---------------
scheduler_events = {
	"cron": {
		"0 */1 * * *": [
			"fertility_suite.storage_tank_management.doctype.storage_tank.storage_tank.check_all_tank_alerts",
		],
	},
	"daily": [
		"fertility_suite.analytics_and_kpi_engine.kpi_engine.generate_daily_kpi_snapshot",
		"fertility_suite.executive_dashboards.dashboard_engine.generate_clinical_dashboard_snapshot",
		"fertility_suite.notification_engine.notification_engine.send_pregnancy_test_reminders",
		"fertility_suite.notification_engine.notification_engine.send_appointment_reminders",
	],
	"weekly": [
		"fertility_suite.executive_dashboards.dashboard_engine.generate_weekly_executive_snapshot",
	],
}

# Fixtures
# --------
fixtures = [
	{"dt": "Role", "filters": [["role_name", "in", [
		"Fertility Doctor",
		"Embryologist",
		"IVF Coordinator",
		"Fertility Nurse",
		"Insurance Officer",
		"Clinic Manager",
		"Fertility Patient",
	]]]},
	{"dt": "Workflow", "filters": [["document_type", "in", ["Fertility Case", "Treatment Plan", "IVF Cycle"]]]},
	{"dt": "Workflow State"},
	{"dt": "Workflow Action Master"},
	{"dt": "Notification Template"},
	{"dt": "Number Card", "filters": [["name", "in", [
		"Active Fertility Cases",
		"Active IVF Cycles",
		"Total Embryos",
		"Frozen Embryos",
		"Pending Insurance Claims",
	]]]},
	{"dt": "Dashboard Chart", "filters": [["name", "in", [
		"IVF Cycle Stage Distribution",
		"Embryo Inventory Status",
	]]]},
]

# Website route rules for the Patient Portal
# -------------------------------------------
website_route_rules = [
	{"from_route": "/fertility-portal/<path:app_path>", "to_route": "fertility-portal"},
]

# Portal menu items surfaced for the Patient role
portal_menu_items = [
	{"title": "IVF Progress", "route": "/fertility-portal/ivf-progress", "reference_doctype": "IVF Cycle", "role": "Fertility Patient"},
	{"title": "Embryo Status", "route": "/fertility-portal/embryo-status", "reference_doctype": "Embryo Inventory", "role": "Fertility Patient"},
	{"title": "Treatment Plans", "route": "/fertility-portal/treatment-plans", "reference_doctype": "Treatment Plan", "role": "Fertility Patient"},
]

# Jinja
# -----
jinja = {
	"methods": [
		"fertility_suite.utils.kpi_utils.get_kpi_value",
	],
}

# Permissions
# -----------
permission_query_conditions = {
	"Fertility Case": "fertility_suite.fertility_case_management.doctype.fertility_case.fertility_case.get_permission_query_conditions",
	"IVF Cycle": "fertility_suite.ivf_cycle_management.doctype.ivf_cycle.ivf_cycle.get_permission_query_conditions",
	"Embryo Inventory": "fertility_suite.embryo_inventory.doctype.embryo_inventory.embryo_inventory.get_permission_query_conditions",
}

has_permission = {
	"Fertility Case": "fertility_suite.fertility_case_management.doctype.fertility_case.fertility_case.has_permission",
	"IVF Cycle": "fertility_suite.ivf_cycle_management.doctype.ivf_cycle.ivf_cycle.has_permission",
	"Embryo Inventory": "fertility_suite.embryo_inventory.doctype.embryo_inventory.embryo_inventory.has_permission",
}

# Testing
# -------
before_tests = "fertility_suite.setup.install.before_tests"

# App installation
# -----------------
after_install = "fertility_suite.setup.install.after_install"
after_migrate = "fertility_suite.setup.install.set_default_home_page"
