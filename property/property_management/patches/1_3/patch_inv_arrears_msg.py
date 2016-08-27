import frappe
from frappe.utils import flt, fmt_money

'''
Adds arrears note to all invoices tenancy invoices.
'''


def execute():
    inv_list = frappe.get_list('Sales Invoice', fields=["*"],
                               filters=[["tenancy_contract", "!=", ""]])
    for inv in inv_list:
        doc = frappe.get_doc("Sales Invoice", inv.name)
        if doc.docstatus == 2 or doc.is_return == 1:
            continue
        arrears = frappe.db.sql("select sum(outstanding_amount) from `tabSales Invoice` where customer = %s "
                                "and docstatus = 1 and due_date < %s and tenancy_contract = %s and is_return != 1 "
                                "and outstanding_amount > 0",
                                (doc.customer, doc.creation, doc.tenancy_contract))[0][0]
        if arrears is None or arrears <= 0:
            note = ""
        else:
            note = "You have {0} in pending arrears, your total amount to pay is: {1}" \
                .format(fmt_money(arrears, 2, doc.currency), fmt_money(flt(doc.outstanding_amount + arrears),
                                                                       2, doc.currency))
        doc.db_set("arrears_note", note, False)

    frappe.db.commit()
    frappe.clear_cache()
