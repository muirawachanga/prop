from __future__ import unicode_literals
import frappe

'''
Update the period start and period to with the current existing ranges of invoices / expenses
'''

def execute():
    lr_list = frappe.get_list('Landlord Remittance', fields=["name"])

    for n in lr_list:
        min_inv_date = frappe.db.sql("""select min(invoice_date) as min_d from (
                                        select invoice_date from `tabLandlord Expense Invoices` where parent = '%s'
                                        union
                                        select invoice_date from `tabLandlord Collection Invoices` where parent = '%s') as invoices;"""
                                        %(n.name, n.name), as_dict=True)
        max_inv_date = frappe.db.sql("""select max(invoice_date) as max_d from (
                                        select invoice_date from `tabLandlord Expense Invoices` where parent = '%s'
                                        union
                                        select invoice_date from `tabLandlord Collection Invoices` where parent = '%s') as invoices;"""
                                        %(n.name, n.name), as_dict=True)

        ps = min_inv_date[0]["min_d"]
        pe = max_inv_date[0]["max_d"]

        lr = frappe.get_doc('Landlord Remittance', n.name)
        if ps and not lr.period_start:
            lr.db_set('period_start', ps, update_modified=False)
        if pe and not lr.period_end:
            lr.db_set('period_end', pe, update_modified=False)

    frappe.db.commit()
