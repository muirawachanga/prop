from __future__ import unicode_literals

import frappe

'''
Customize Journal Entry Account Form to include Remittance Payment Voucher type in the reference_type field.
'''


def execute():
    cf = frappe.new_doc('Customize Form')
    cf.doc_type = 'Journal Entry Account'
    cf.fetch_to_customize()
    curr_options = cf.get_existing_property_value('options', 'reference_type')
    cf.make_property_setter('options', curr_options + '\nRemittance Payment Voucher', 'Text', 'reference_type')
    frappe.db.commit()
    frappe.clear_cache()
