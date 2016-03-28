// Copyright (c) 2016, Bituls Company Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('Tenancy Contract', {
  refresh: function(frm) {
    if (frm.doc.status == 'Active') {
      frm.add_custom_button(__("Create Invoice"), function() {
        frm.events.make_invoice(frm)
      }).addClass("btn-primary");
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
