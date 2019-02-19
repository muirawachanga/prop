// Copyright (c) 2019, Bituls Company Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('Hand Over', {
	onload: function(frm) {
	frm.set_query('tenancy_contract', function(){
            return {
                query: "property.property_management.doctype.hand_over.hand_over.tenancy_contract_query",
                filters: {
                    tc_filters: ['In Progress', 'Completed'],
                    side: 'not in'
                }
            }
    });

	}
});
