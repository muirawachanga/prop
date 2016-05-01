// Copyright (c) 2016, Bituls Company Limited and contributors
// For license information, please see license.txt

//cur_frm.add_fetch("owner_contract", "property_name", "property_name" );

frappe.ui.form.on('Landlord Remittance', {
  setup: function(frm) {

  },

  onload: function(frm) {

  },

  refresh: function(frm) {
    //frm.disable_save();
  },

	owner_contract: function(frm) {
    frm.fields_dict.load_remittance_data.$input.addClass("btn-primary");
	},

  include_unpaid_invoices: function(frm) {
    frm.fields_dict.load_remittance_data.$input.addClass("btn-primary");
	},

  load_remittance_data: function(frm) {
    return frappe.call({
      method: "get_details",
      doc: frm.doc,
      callback: function(r, rt) {
        frm.fields_dict.load_remittance_data.$input.removeClass("btn-primary");
        frm.refresh()
      }
    });
  },
});
