// Copyright (c) 2016, Bituls Company Limited and contributors
// For license information, please see license.txt

//cur_frm.add_fetch("owner_contract", "property_name", "property_name" );

frappe.ui.form.on('Landlord Remittance', {
    setup: function(frm) {

    },

    onload: function(frm) {
        if (!frm.doc.collection_period_start || !frm.doc.collection_period_end) {
            var today = new Date();
            var start_date = new Date(today.getFullYear(), today.getMonth(), 1);
            var end_date = new Date(today.getFullYear(), today.getMonth() + 1, 0);
            //Set only if not set
            if (!frm.doc.collection_period_start) {
                frm.set_value('collection_period_start', start_date);
            }
            if (!frm.doc.collection_period_end) {
                frm.set_value('collection_period_end', end_date);
            }
            if (!frm.doc.expense_period_start) {
                frm.set_value('expense_period_start', start_date);
            }
            if (!frm.doc.expense_period_end) {
                frm.set_value('expense_period_end', end_date);
            }
        }
    },

    make_payment: function (frm) {
        frappe.model.open_mapped_doc({
            frm: frm,
            method: "property.property_management.doctype.landlord_remittance.landlord_remittance.pay_remittance"
        })
    },

    refresh: function(frm) {
        if (frm.doc.payment_status == 'Pending' && frm.doc.docstatus == 1) {
            frm.add_custom_button(__("Make Payment"), function () {
                frm.events.make_payment(frm);
            }).addClass("btn-primary");
        }
    },

    owner_contract: function(frm) {
        return frappe.call({
            method: "init_values",
            doc: frm.doc,
            callback: function(r, rt) {
                frm.fields_dict.load_remittance_data.$input.addClass("btn-primary");
                frm.refresh()
            }
        });
    },

    include_unpaid_invoices: function(frm) {
        frm.fields_dict.load_remittance_data.$input.addClass("btn-primary");
    },

    load_remittance_data: function(frm) {
        if (frm.doc.expense_period_start > frm.doc.expense_period_end) {
            msgprint(__('Expense period start is greater than period end. Cannot load.'));
            return;
        }
        if (frm.doc.collection_period_start > frm.doc.collection_period_end) {
            msgprint(__('Collections period start is greater than period end. Cannot load.'));
            return;
        }
        return frappe.call({
            method: "get_details",
            doc: frm.doc,
            callback: function(r, rt) {
                frm.fields_dict.load_remittance_data.$input.removeClass("btn-primary");
                frm.refresh()
            }
        });
    },
    expense_period_start: function(frm) {
        frm.fields_dict.load_remittance_data.$input.addClass("btn-primary");
    },
    expense_period_end: function(frm) {
        frm.fields_dict.load_remittance_data.$input.addClass("btn-primary");
    }
});

cur_frm.cscript.lookup_obj = function lookup(array, prop, value) {
    for (var i = 0, len = array.length; i < len; i++)
        if (array[i] && array[i][prop] === value) return array[i];
}

cur_frm.cscript.recalculate_collections = function(frm, cdt, cdn) {
    var ci = frm.doc.collection_invoices;
    var cd = frm.doc.collections_details; //Invoice item
    var lci_doc = frm.fields_dict["collection_invoices"].grid.grid_rows_by_docname[cdn].doc;
    var cel = cur_frm.cscript.lookup_obj(frm.doc.remittance_summary, "description", "Commission Eligible Collections");
    //Remove all the items whose invoice has been removed.
    frm.fields_dict["collections_details"].df.read_only = 0;
    frm.refresh_field("collections_details");
    $.each(cd, function(i, obj) {
        if (obj.invoice === lci_doc.invoice) {
            //Remove this inv item from the total commision eligible. (base amt)
            if (obj.is_remittable && !obj.remit_full_amount) {
                cel.amount = flt(cel.amount) - flt(obj.item_total);
            }
            frm.fields_dict["collections_details"].grid.grid_rows_by_docname[obj.name].remove();
        }
    });
    frm.fields_dict["collections_details"].df.read_only = 1;
    frm.refresh_field("collections_details");
    frm.doc.remittable_collections = flt(frm.doc.remittable_collections) - flt(lci_doc.remittance_amount);
    frm.doc.total_collections = flt(frm.doc.total_collections) - flt(lci_doc.grand_total);
    cur_frm.cscript.lookup_obj(frm.doc.remittance_summary, "description", "Total Collections").amount = frm.doc.total_collections;
    cur_frm.cscript.lookup_obj(frm.doc.remittance_summary, "description", "Remittable Collections").amount = frm.doc.remittable_collections;

    var base_amt = flt(cel.amount);
    cur_frm.cscript.lookup_obj(frm.doc.remittance_summary, "description", "Commission Exempted Collections").amount = flt(frm.doc.remittable_collections) - base_amt;

    // Calculate commission and remmitance
    var cr = flt(frm.doc.commission_rate / 100);
    var ca = flt(base_amt * cr);
    frm.doc.management_fee = ca;
    var net_rem = flt(frm.doc.remittable_collections - flt(frm.doc.management_fee + frm.doc.deductible_expenses));
    frm.doc.remittance_amount = net_rem;
    cur_frm.cscript.lookup_obj(frm.doc.remittance_summary, "description", "Commission Charged").amount = frm.doc.management_fee;
    cur_frm.cscript.lookup_obj(frm.doc.remittance_summary, "description", "Net Amount To Landlord").amount = net_rem;

    frm.refresh_fields();

}

cur_frm.cscript.recalculate_expenses = function(frm, cdt, cdn) {
    var ei = frm.doc.expense_invoices;
    var ed = frm.doc.expense_details; //Invoice item
    var lei_doc = frm.fields_dict["expense_invoices"].grid.grid_rows_by_docname[cdn].doc;
    //Remove all the items whose invoice has been removed.
    frm.fields_dict["expense_details"].df.read_only = 0;
    frm.refresh_field("expense_details");
    $.each(ed, function(i, obj) {
        if (obj.invoice === lei_doc.invoice) {
            frm.fields_dict["expense_details"].grid.grid_rows_by_docname[obj.name].remove();
        }
    });
    frm.fields_dict["expense_details"].df.read_only = 1;
    frm.refresh_field("expense_details");

    // Reduce Total Expenses and Deductible Expenses
    frm.doc.total_expenses = flt(frm.doc.total_expenses) - flt(lei_doc.grand_total);
    frm.doc.deductible_expenses = flt(frm.doc.deductible_expenses) - flt(lei_doc.deduction_amount);

    cur_frm.cscript.lookup_obj(frm.doc.remittance_summary, "description", "Total Expenses").amount = frm.doc.total_expenses;
    cur_frm.cscript.lookup_obj(frm.doc.remittance_summary, "description", "Deductible Expenses").amount = frm.doc.deductible_expenses;

    // Net Amount To Landlord
    var net = flt(frm.doc.remittable_collections) - (flt(frm.doc.management_fee) + flt(frm.doc.deductible_expenses));
    cur_frm.cscript.lookup_obj(frm.doc.remittance_summary, "description", "Net Amount To Landlord").amount = net;
    frm.doc.remittance_amount = net;

    frm.refresh_fields();

}


frappe.ui.form.on('Landlord Expense Invoices', 'expense_invoices_remove', function(frm, cdt, cdn) {
    cur_frm.cscript.recalculate_expenses(frm, cdt, cdn);
});

frappe.ui.form.on('Landlord Collection Invoices', 'collection_invoices_remove', function(frm, cdt, cdn) {
    cur_frm.cscript.recalculate_collections(frm, cdt, cdn);
});
