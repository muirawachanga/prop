# -*- coding: utf-8 -*-
# Copyright (c) 2016, Bituls Company Limited and contributors
# For license information, please see license.txt


from __future__ import unicode_literals

import frappe
from property.property_management import utils

'''
Add Billing Period to existing invoices.
'''


def execute():

    """ Don't proceed if Billing Period Field does not exist.
        Bench will run patch before running the fixture to create the custom field.
    """
    bp_field = frappe.get_doc('Custom Field', 'Sales Invoice-billing_period')
    if not bp_field:
        frappe.log('Missing Sales Invoice-billing_period Custom Field. Aborting patch add_billing_period')
        return

    invoices = frappe.get_all("Sales Invoice",
                              fields=["name", "ifnull(tenancy_contract, '')", "ifnull(billing_period, '')"],
                              filters=[["tenancy_contract", "!=", ""],
                                       ["docstatus", "!=", 2],
                                       ["billing_period", "=", ""]],
                              order_by="creation desc", limit_page_length=3000)
    for inv in invoices:
        doc = frappe.get_doc("Sales Invoice", inv.name)
        utils.create_period_if_not_exists(doc.due_date, "Monthly")
        pn = utils.get_billing_period_for_date(doc.due_date, "Monthly")
        if not pn:
            raise frappe.DataError("No Billing Period Found! Invoice: {}".format(doc.name))
        doc.db_set("billing_period", pn, False)

    frappe.db.commit()
