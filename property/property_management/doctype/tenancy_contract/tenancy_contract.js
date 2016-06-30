// Copyright (c) 2016, Bituls Company Limited and contributors
// For license information, please see license.txt

var lock_tc_items = 1;
var loaded_tc_items = [];

frappe.ui.form.on('Tenancy Contract', {
    onload: function(frm) {
        return frappe.call({
            method: "property.property_management.doctype.property_management_settings.property_management_settings.load_configuration",
            args: {
                "name": 'lock_tenancy_contract_items',
                "default": 1
            },
            callback: function(r, rt) {
                if (r) {
                    lock_tc_items = r.message;
                } else {
                    msgprint(__("Failed to load required configuration! Please contact support."), __("Warning!"));
                }
            }
        });
    },
    refresh: function(frm) {
        if (frm.doc.contract_status == 'Active' || frm.doc.contract_status == 'Suspended') {
            frm.add_custom_button(__("Create Invoice"), function() {
                frm.events.make_invoice(frm)
            }).addClass("btn-primary");
        }

        if (frm.doc.contract_status != "New") {
            frm.toggle_enable('*', 0);
            if (frm.doc.contract_status != 'Terminated') {
                frm.toggle_enable(['items', 'grace_period', 'auto_generate_invoice', 'email_invoice', 'taxes_and_charges', 'taxes', 'termination_date'], 1);
            }
            //frm.disable_save();
        }
        //Load current tc item names to validate if user will change them.
        $.each(frm.doc.items, function(i, o) {
            loaded_tc_items.push(o.name);
        });
    },
    validate: function(frm) {
        if (!frm.doc.start_date && frm.doc.contract_status == "Active") {
            msgprint(__("You must set the contract start date before approving"));
            validated = false;
            return
        }
        if (!frm.doc.end_date && frm.doc.contract_status == "Active") {
            msgprint(__("You must set the contract end date before approving"));
            validated = false;
            return
        }
        if (!frm.doc.termination_date && frm.doc.contract_status == "Terminated") {
            msgprint(__("Please set the contract termination date."));
            validated = false;
            return;
        }
        if (!frm.doc.cancellation_date && frm.doc.contract_status == "Cancelled") {
            frm.set_value('cancellation_date', get_today());
            validated = true;
        }

        if (frm.doc.contract_status != "New") {
          if (lock_tc_items) {
            var items = frm.doc.items;
            for (var i = 0; i < items.length; i++) {
                if ($.inArray(items[i].name, loaded_tc_items) == -1) {
                    msgprint(__("You cannot add a new billing item to a contract in Active status. Not Saved."));
                    validated = false;
                    return;
                }
            }
            if (items.length != loaded_tc_items.length) {
                msgprint(__("You cannot remove billing items from a contract in Active status. Not Saved."));
                validated = false;
                return;
            }
          }
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
    end_date: function(frm) {
        if (frm.doc.start_date) {
            if (frappe.datetime.get_diff(frm.doc.start_date, frm.doc.end_date) > 0) {
                msgprint(__('End date cannot be earlier than start date.'));
                frm.set_value('end_date', '');
            }
            if (frappe.datetime.get_diff(frm.doc.date_of_first_billing, frm.doc.end_date) > 0) {
                msgprint(__('End date cannot be earlier than Date of First Billing.'));
                frm.set_value('end_date', '');
            }
        }
    },
    date_of_first_billing: function(frm) {
        if (frm.doc.start_date) {
            if (frappe.datetime.get_diff(frm.doc.start_date, frm.doc.date_of_first_billing) > 0) {
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
};
