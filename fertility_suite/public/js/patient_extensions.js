frappe.ui.form.on("Patient", {
	refresh(frm) {
		if (frm.doc.__islocal) {
			return;
		}
		frm.add_custom_button(
			__("New Fertility Case"),
			() => {
				frappe.new_doc("Fertility Case", { patient: frm.doc.name });
			},
			__("Create")
		);

		frappe.db
			.count("Fertility Case", {
				filters: { patient: frm.doc.name, status: ["not in", ["Closed", "Cancelled"]] },
			})
			.then((count) => {
				if (count) {
					frm.dashboard.add_indicator(__("Active Fertility Cases: {0}", [count]), "orange");
				}
			});
	},
});
