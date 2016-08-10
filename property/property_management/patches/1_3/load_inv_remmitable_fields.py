from __future__ import unicode_literals
import frappe

'''
Added new fields for remittable flags to invoices. We load it for existing invoices here.
'''

def execute():
    inv_list = frappe.get_list('Sales Invoice', fields=["name", "tenancy_contract"], filters=[["tenancy_contract", "!=", ""]])
    for inv in inv_list:
        s_items = frappe.get_list('Sales Invoice Item', fields=['*'], filters={"parent": inv.name})
        for si in s_items:
            ti = frappe.get_list('Tenancy Contract Item', fields=['*'], filters={"item_code": si.item_code, "parent": inv.tenancy_contract})
            if not len(ti):
                continue
            si_doc = frappe.get_doc('Sales Invoice Item', si.name)
            si_doc.db_set("remittable", ti[0].remmitable)
            si_doc.db_set("remit_full_amount", ti[0].remit_full_amount)

    frappe.db.commit()
    frappe.clear_cache()
