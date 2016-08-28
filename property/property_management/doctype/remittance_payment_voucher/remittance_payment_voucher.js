// Copyright (c) 2016, Bituls Company Limited and contributors
// For license information, please see license.txt


frappe.ui.form.on('Remittance Payment Voucher', {
    refresh: function (frm) {
        if (frm.doc.payment_method != "") {
            frm.fields_dict['payment_account'].df.hidden = 0;
            frm.fields_dict['payment_account'].df.reqd = 1;
            frm.refresh_field('payment_account');
        }
        frm.set_query('landlord_remittance', function () {
            return {
                filters: [
                    ['Landlord Remittance', 'docstatus', '=', 1],
                    ['Landlord Remittance', 'payment_status', '=', 'Pending']
                ]
            }
        });
    },
    landlord_remittance: function (frm) {
        if (frm.doc.landlord_remittance) {
            frappe.model.with_doc('Landlord Remittance', frm.doc.landlord_remittance, function (name, lr) {
                if (lr && lr.docs) {
                    frm.set_value("owner_contract", lr.docs[0].owner_contract);
                    frm.set_value("property_name", lr.docs[0].property_name);
                    frm.set_value("landlord_name", lr.docs[0].owner_name);
                    frm.set_value("net_remittance_amount", lr.docs[0].remittance_amount);
                    frm.set_value("amount_paid", lr.docs[0].remittance_amount);
                    frm.set_value("management_fee", lr.docs[0].management_fee);
                    frm.set_value("deductible_expenses", lr.docs[0].deductible_expenses);
                    frappe.model.with_doc('Owner Contract', lr.docs[0].owner_contract, function (name, owc) {
                        if (owc && owc.docs) {
                            frappe.model.with_doc('Property', owc.docs[0].property, function (name, p) {
                                if (p && p.docs) {
                                    frm.set_value("trust_fund_account", p.docs[0].trust_fund_account);
                                }
                            });
                        }
                    });
                }
            });
        }
    },
    payment_method: function (frm) {
        if (frm.doc.payment_method) {
            frm.set_value('payment_account', '');
            if (frm.doc.payment_method === 'Cash') {
                frm.set_query('payment_account', function () {
                    return {
                        filters: [
                            ['Account', 'account_type', '=', 'Cash'],
                            ['Account', 'company', '=', frm.doc.company],
                            ['Account', 'is_group', '=', 0]
                        ]
                    }
                });
                frm.fields_dict['payment_account'].df.hidden = 0;
                frm.fields_dict['payment_account'].df.reqd = 1;
                frm.refresh_field('payment_account');
                frm.fields_dict['reference_number'].df.reqd = 0;
                frm.refresh_field('reference_number');
                frm.fields_dict['reference_date'].df.reqd = 0;
                frm.refresh_field('reference_date');
            }
            if (frm.doc.payment_method === 'Bank') {
                frm.set_query('payment_account', function () {
                    return {
                        filters: [
                            ['Account', 'account_type', '=', 'Bank'],
                            ['Account', 'company', '=', frm.doc.company],
                            ['Account', 'is_group', '=', 0]
                        ]
                    }
                });
                frm.fields_dict['payment_account'].df.hidden = 0;
                frm.fields_dict['payment_account'].df.reqd = 1;
                frm.refresh_field('payment_account');
                frm.fields_dict['reference_number'].df.reqd = 1;
                frm.refresh_field('reference_number');
                frm.fields_dict['reference_date'].df.reqd = 1;
                frm.refresh_field('reference_date');
            }
        }
        if (frm.doc.payment_method === '') {
            frm.fields_dict['payment_account'].df.hidden = 1;
            frm.fields_dict['payment_account'].df.reqd = 0;
            frm.refresh_field('payment_account');
            frm.fields_dict['reference_number'].df.reqd = 0;
            frm.refresh_field('reference_number');
            frm.fields_dict['reference_date'].df.reqd = 0;
            frm.refresh_field('reference_date');
        }
    }
});
