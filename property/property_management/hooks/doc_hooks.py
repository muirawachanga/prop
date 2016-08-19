from __future__ import unicode_literals

import frappe


def sales_invoice_arrears(doc, event):
    arrears = frappe.db.sql("select sum(outstanding_amount) from `tabSales Invoice` where customer = %s "
                            "and docstatus = 1 and name <> %s;", (doc.customer, doc.name or ''))[0][0]
    if arrears is None:
        return
    doc.outstanding_arrears = arrears
