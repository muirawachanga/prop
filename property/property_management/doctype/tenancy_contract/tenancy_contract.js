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
