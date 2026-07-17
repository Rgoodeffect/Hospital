frappe.pages["fertility-command-center"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Fertility Command Center"),
		single_column: true,
	});

	new fertility_suite.CommandCenterDashboard(wrapper);
};
