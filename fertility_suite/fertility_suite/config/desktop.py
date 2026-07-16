from frappe import _


def get_data():
	return [
		{
			"module_name": "Fertility Case Management",
			"category": "Modules",
			"label": _("Fertility Case Management"),
			"color": "#e83e8c",
			"icon": "octicon octicon-heart",
			"type": "module",
			"description": "Manage fertility patient cases end to end.",
		},
		{
			"module_name": "IVF Cycle Management",
			"category": "Modules",
			"label": _("IVF Cycle Management"),
			"color": "#7c4dff",
			"icon": "octicon octicon-pulse",
			"type": "module",
			"description": "Plan and track IVF cycles from stimulation to pregnancy test.",
		},
		{
			"module_name": "Embryology Management",
			"category": "Modules",
			"label": _("Embryology Management"),
			"color": "#00bcd4",
			"icon": "octicon octicon-beaker",
			"type": "module",
			"description": "Fertilization outcomes and embryo development tracking.",
		},
		{
			"module_name": "Embryo Bank",
			"category": "Modules",
			"label": _("Embryo Bank"),
			"color": "#009688",
			"icon": "octicon octicon-database",
			"type": "module",
			"description": "Embryo inventory and cryogenic storage management.",
		},
		{
			"module_name": "Insurance Management",
			"category": "Modules",
			"label": _("Insurance Management"),
			"color": "#ff9800",
			"icon": "octicon octicon-shield",
			"type": "module",
			"description": "Insurance plans, pre-authorizations and claims.",
		},
		{
			"module_name": "Executive Dashboards",
			"category": "Modules",
			"label": _("Executive Dashboards"),
			"color": "#3f51b5",
			"icon": "octicon octicon-graph",
			"type": "module",
			"description": "KPIs and executive reporting.",
		},
	]
