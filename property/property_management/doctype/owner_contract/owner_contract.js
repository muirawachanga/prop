// Copyright (c) 2016, Bituls Company Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('Owner Contract', {
	refresh: function(frm) {
		if(frm.doc.status == "Cancelled" || frm.doc.status == "Terminated" || frm.doc.status == "Active"){
				frm.set_df_property("start_date", "read_only", 1);
				frm.set_df_property("end_date", "read_only", 1);
				frm.set_df_property("property", "read_only", 1);
				frm.set_df_property("owner_customer", "read_only", 1);
				frm.set_df_property("owner_supplier", "read_only", 1);
				frm.set_df_property("commision", "read_only", 1);
		}
		if(frm.doc.status == "Cancelled" || frm.doc.status == "Terminated"){
				frm.set_df_property("termination_date", "read_only", 1);
		}
	},
	validate: function(frm) {
		if (!frm.doc.start_date && frm.doc.status == "Active"){
			msgprint(__("You must set the contract start date before approving"));
			validated = false;
			return
		}
		if (!frm.doc.end_date && frm.doc.status == "Active"){
			msgprint(__("You must set the contract end date before approving"));
			validated = false;
			return
		}
		if (!frm.doc.termination_date && frm.doc.status == "Terminated"){
			msgprint(__("You must set the termination date before terminating"));
			validated = false;
		}
	}
});
