from __future__ import unicode_literals
import frappe

'''
Wrong Landlord Remittance Series values after the change to use prefix LAR- and autonaming.
Need to delete in Property Setter and also insert proper series value in tabSeries
'''

def execute():
    pref = 'LAR-'
    frappe.db.sql("delete from `tabProperty Setter` where name='Landlord Remittance-naming_series-options'")
    lr_list = frappe.get_list('Landlord Remittance', fields=["name"], filters=[], order_by="creation desc")
    if len(lr_list):
        val = int(lr_list[0].name.replace(pref, ''))
        frappe.db.sql("insert into tabSeries (name, current) values (%s, %s)", (pref, str(val)))
    frappe.db.commit()
    frappe.clear_cache()
