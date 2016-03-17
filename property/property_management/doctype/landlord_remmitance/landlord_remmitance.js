// Copyright (c) 2016, Bituls Company Limited and contributors
// For license information, please see license.txt

//cur_frm.add_fetch("owner_contract", "customer_name", "owner_name" );

frappe.ui.form.on('Landlord Remmitance', {
  setup: function(frm) {

  },

  onload: function(frm) {

  },

  refresh: function(frm) {
    frm.disable_save();
  },

	owner_contract: function(frm) {
		frm.fields_dict.get_relevant_entries.$input.addClass("btn-primary");
	},

  pay_remittances: function(frm) {
		//frm.fields_dict.get_relevant_entries.$input.removeClass("btn-primary");
  },
  get_relevant_entries: function(frm) {
    return frappe.call({
      method: "get_details",
      doc: frm.doc,
      callback: function(r, rt) {
        frm.refresh()
				frm.fields_dict.get_relevant_entries.$input.removeClass("btn-primary");
				frm.fields_dict.pay_remittances.$input.addClass("btn-primary");
      }
    });
  }
});
