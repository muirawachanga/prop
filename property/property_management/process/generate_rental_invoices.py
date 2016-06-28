# -*- coding: utf-8 -*-
# Copyright (c) 2015, Bituls Company Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, add_months, date_diff, add_days, nowdate, get_datetime_str
from frappe.model.mapper import get_mapped_doc, _

logger = frappe.get_logger()


def process_contract(contract):
    c_doc = frappe.get_doc("Tenancy Contract", contract.name)
    if not len(c_doc.items):
        logger.warn(
            "Skipping generating invoice for contract %s because it has no billing items", (contract.name,))
        return

    def postprocess(source, target):
        set_missing_values(source, target)
        # Get the advance paid Journal Entries in Sales Invoice Advance
        target.get_advances()

    def set_missing_values(source, target):
        target.is_pos = 0
        target.ignore_pricing_rule = 1
        target.flags.ignore_permissions = True
        target.run_method("set_missing_values")
        target.run_method("calculate_taxes_and_totals")

    def update_item(source, target, source_parent):
        target.amount = flt(source.qty) * flt(source.rate)
        target.base_aunt = target.amount
        target.qty = source.qty

    logger.debug('Generating invoice...')
    doclist = get_mapped_doc("Tenancy Contract", contract.name, {
        "Tenancy Contract": {
            "doctype": "Sales Invoice",
            "field_map": {
                "party_account_currency": "party_account_currency",
                "property_unit_name": "property_unit"
            },
            "validation": {
                "contract_status": ["=", "Active"]
            }
        },
        "Tenancy Contract Item": {
            "doctype": "Sales Invoice Item"
        },
        "Sales Taxes and Charges": {
            "doctype": "Sales Taxes and Charges",
            "add_if_empty": True
        }
    }, None, postprocess, ignore_permissions=True)
    logger.debug("Invoice for contract %s generated successfully.", contract.name)
    doclist.save()

def daily():
    today = nowdate()
    logger.debug("Begin rental invoice generation processing on %s", (today,))
    contracts = frappe.get_list('Tenancy Contract', fields=['*'], filters={'contract_status': 'Active'})
    logger.debug("Loaded %s active contracts for processing", str(len(contracts)))
    for c in contracts:
        logger.debug("Processing contract id: %s  %s", c.name, c.customer)
        process_contract(c)

    frappe.db.commit()
