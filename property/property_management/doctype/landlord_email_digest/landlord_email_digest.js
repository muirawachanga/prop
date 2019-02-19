// Copyright (c) 2018, Bituls Company Limited and contributors
// For license information, please see license.txt

cur_frm.cscript.refresh = function(doc, dt, dn) {
	doc = locals[dt][dn];
	var save_msg = __("You must Save the form before proceeding");
	var err_msg = __("There was an error. One probable reason could be that you haven't saved the form. Please contact support@erp.com if the problem persists.")
    cur_frm.set_query('landlord', function(){
        return {
            query: "property.property_management.doctype.landlord_email_digest.landlord_email_digest.landlord_query",
            filters: {
                tc_filters: [1],
                side: 'not in'
            }
        }
    });
	cur_frm.add_custom_button(__('View Now'), function() {
		frappe.call({
			method: 'property.property_management.doctype.landlord_email_digest.landlord_email_digest.get_digest_msg',
			args: {
				name: doc.name
			},
			callback: function(r) {
				var d = new frappe.ui.Dialog({
					title: __('Email Digest: ') + dn,
					width: 800
				});
				$(d.body).html(r.message);
				d.show();
			}
		});
	}, "fa fa-eye-open", "btn-default");

	if(frappe.session.user==="Administrator") {
		cur_frm.add_custom_button(__('Send Now'), function(frm) {
			doc = locals[dt][dn];
			if(doc.__unsaved != 1) {
				return $c_obj(doc, 'send', '', function(r, rt) {
					if(r.exc) {
						frappe.msgprint(err_msg);
						console.log(r.exc);
					} else {
						//console.log(arguments);
						frappe.msgprint(__('Message Sent'));
					}
				});
			} else {
				frappe.msgprint(save_msg);
			}
		}, "fa fa-envelope", "btn-default");
	}
}

cur_frm.cscript.add_to_rec_list = function(doc, dialog, length) {
	// add checked users to list of recipients
	var rec_list = [];
	$(dialog).find('input:checked').each(function(i, input) {
		rec_list.push($(input).attr('data-id'));
	});

	doc.recipient_list = rec_list.join('\n');
	cur_frm.rec_dialog.hide();
	cur_frm.save();
	cur_frm.refresh_fields();
}
