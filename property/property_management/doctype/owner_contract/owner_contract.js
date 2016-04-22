// Copyright (c) 2016, Bituls Company Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('Owner Contract', {
	refresh: function(frm) {
		if(frm.doc.contract_status == "Cancelled" || frm.doc.contract_status == "Terminated" || frm.doc.contract_status == "Active"
			|| frm.doc.contract_status == "Rejected"){
				frm.toggle_enable('*',0);
				frm.disable_save();
		}
	},
	validate: function(frm) {
		if (!frm.doc.start_date && frm.doc.contract_status == "Active"){
			msgprint(__("You must set the contract start date before approving"));
			validated = false;
			return
		}
		if (!frm.doc.end_date && frm.doc.contract_status == "Active"){
			msgprint(__("You must set the contract end date before approving"));
			validated = false;
			return
		}
		if (!frm.doc.termination_date && frm.doc.contract_status == "Terminated"){
			frm.set_value('terminated_date', get_today());
			validated = true;
		}
		if (!frm.doc.cancellation_date && frm.doc.contract_status == "Cancelled"){
			frm.set_value('cancellation_date', get_today());
			validated = true;
		}
	}
});
