# -*- coding: utf-8 -*-
# Copyright (c) 2015, Bituls Company Limited and contributors
# For license information, please see license.txt

'''
Patch Landlord Remittance after adding an autonaming column and period start and end.
'''

from __future__ import unicode_literals
import frappe

def execute():
    lr_list = frappe.get_list('Landlord Remittance', fields=["name"], filters={"name": ("not like", "LAR-%")}, order_by="creation")

    start_val = 1
    prefix = 'LAR-'
    for n in lr_list:
        #Update the period start and period to with the current existing ranges of invoices / expenses
        min_inv_date = frappe.db.sql("""select min(invoice_date) as min_d from `tabLandlord Collection Invoices` ci where parent = '%s';"""
                                     %(n.name), as_dict=True)
        max_inv_date = frappe.db.sql("""select max(invoice_date) as max_d from `tabLandlord Collection Invoices` ci where parent = '%s';"""
                                     %(n.name), as_dict=True)
        min_exp_date = frappe.db.sql("""select min(invoice_date) as min_d from `tabLandlord Expense Invoices` ci where parent = '%s';"""
                                     %(n.name), as_dict=True)
        max_exp_date = frappe.db.sql("""select max(invoice_date) as max_d from `tabLandlord Expense Invoices` ci where parent = '%s';"""
                                     %(n.name), as_dict=True)

        ps = min_inv_date[0]["min_d"] if min_inv_date[0]["min_d"] < min_exp_date[0]["min_d"] else min_exp_date[0]["min_d"]
        pe = max_inv_date[0]["max_d"] if max_inv_date[0]["max_d"] > max_exp_date[0]["max_d"] else max_exp_date[0]["max_d"]

        lr = frappe.get_doc('Landlord Remittance', n.name)
        lr.db_set('period_start', ps, update_modified=False)
        lr.db_set('period_end', pe, update_modified=False)

        #Rename doc
        new_name = prefix + str(start_val).zfill(5)
        new_doc = frappe.rename_doc("Landlord Remittance", n.name, new_name, debug=0, force=True)

        start_val = start_val + 1

    frappe.db.commit()
