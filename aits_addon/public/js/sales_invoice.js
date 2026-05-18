frappe.ui.form.on("Sales Invoice", {
	is_return: function(frm) {
		if (frm.doc.is_return) {
			frm.set_value("update_stock", 0);
		}
	}
});