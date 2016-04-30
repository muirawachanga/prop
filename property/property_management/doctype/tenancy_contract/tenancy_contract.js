// Copyright (c) 2016, Bituls Company Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('Tenancy Contract', {

  refresh: function(frm) {
    if (frm.doc.contract_status == 'Active' || frm.doc.contract_status == 'Suspended') {
      frm.add_custom_button(__("Create Invoice"), function() {
        frm.events.make_invoice(frm)
      }).addClass("btn-primary");
    }

		if(frm.doc.contract_status != "New"){
        frm.toggle_enable('*',0);
        frm.toggle_enable(['items','grace_period','auto_generate_invoice', 'email_invoice', 'taxes_and_charges', 'taxes'],1);
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
	},

  make_invoice: function(frm) {
    frappe.model.open_mapped_doc({
      method: "property.property_management.doctype.tenancy_contract.tenancy_contract.make_sales_invoice",
      frm: frm
    })
  },
  start_date: function(frm) {
    if (frm.doc.start_date) {
      frm.set_value('date_of_first_billing', frm.doc.start_date);
      var msg = __('Date of First Billing set to: ') + frm.doc.start_date + __('. Note that you can select a different date if you wish.');
      msgprint(msg);
    } else {

    }
  },
  end_date: function(frm){
    if (frm.doc.start_date) {
      if(frappe.datetime.get_diff(frm.doc.start_date, frm.doc.end_date) > 0){
        msgprint(__('End date cannot be earlier than start date.'));
        frm.set_value('end_date', '');
      }
      if(frappe.datetime.get_diff(frm.doc.date_of_first_billing, frm.doc.end_date) > 0){
        msgprint(__('End date cannot be earlier than Date of First Billing.'));
        frm.set_value('end_date', '');
      }
    }
  },
  date_of_first_billing: function(frm){
    if (frm.doc.start_date) {
      if(frappe.datetime.get_diff(frm.doc.start_date, frm.doc.date_of_first_billing) > 0){
        msgprint(__('Date of First Billing cannot be earlier than start date.'));
        frm.set_value('date_of_first_billing', '');
      }
    }
  },
  property_unit: function(frm) {
    if (!frm.doc.property_unit) {
      frm.set_value("property_name", "");
      frm.set_value("property_unit_name", "");
    }
    frappe.model.get_value("Property Unit", frm.doc.property_unit, "property", function(value) {
      frappe.model.with_doc("Property", value.property, function(r) {
        var p = frappe.model.get_doc("Property", value.property);
        frm.set_value("property_name", p.property_name);
      });
    });
  },
  taxes_and_charges: function(frm) {
    console.log(frm);
  }
});

cur_frm.cscript.item_code = function(doc, cdt, cdn) {
  var d = locals[cdt][cdn];
  if (d.item_code) {
    return frappe.call({
      method: "property.property_management.doctype.tenancy_contract.tenancy_contract.get_item_details",
      args: {
        "item_code": d.item_code
      },
      callback: function(r, rt) {
        if (r.message) {
          $.each(r.message, function(k, v) {
            frappe.model.set_value(cdt, cdn, k, v);
          });
          refresh_field('image_view', d.name, 'items');
        }
      }
    })
  }
}
