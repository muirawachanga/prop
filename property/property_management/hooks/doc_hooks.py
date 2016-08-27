from __future__ import unicode_literals

import frappe
from frappe.utils import flt, fmt_money, today


def sales_invoice_arrears(doc, event):
    # Don't do this for returns
    if doc.is_return == 1:
        return
    # Do this only for rental related invoices.
    if doc.tenancy_contract in (None, ''):
        return
    arrears = frappe.db.sql("select sum(outstanding_amount) from `tabSales Invoice` where customer = %s "
                            "and docstatus = 1 and due_date < %s and tenancy_contract = %s and is_return != 1 "
                            "and outstanding_amount > 0",
                            (doc.customer, today(), doc.tenancy_contract))[0][0]
    if arrears is None or arrears <= 0:
        doc.arrears_note = ""
        return
    doc.arrears_note = "You have {0} in pending arrears, your total amount to pay is: {1}" \
        .format(fmt_money(arrears, 2, doc.currency), fmt_money(flt(doc.outstanding_amount + arrears),
                                                               2, doc.currency))
