frappe.provide("fertility_suite");

fertility_suite.render_status_indicator = function (status) {
	const status_map = {
		Active: "status-active",
		Closed: "status-closed",
		Alert: "status-alert",
	};
	const css_class = status_map[status] || "status-active";
	return `<span class="fertility-status-indicator ${css_class}">${status}</span>`;
};
