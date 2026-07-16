frappe.ui.form.on("Fertility Case", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("New Fertility Assessment"), () => {
				frappe.new_doc("Fertility Assessment", { fertility_case: frm.doc.name, patient: frm.doc.patient });
			});
			frm.add_custom_button(__("New Treatment Plan"), () => {
				frappe.new_doc("Treatment Plan", { fertility_case: frm.doc.name, patient: frm.doc.patient });
			});
			frm.add_custom_button(__("New IVF Cycle"), () => {
				frappe.new_doc("IVF Cycle", { fertility_case: frm.doc.name, patient: frm.doc.patient });
			});
		}
	},
});
