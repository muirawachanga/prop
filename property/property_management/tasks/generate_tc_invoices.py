# -*- coding: utf-8 -*-
# Copyright (c) 2015, Bituls Company Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe.exceptions import ValidationError
from frappe.utils import nowdate, logger, getdate
from property.property_management.doctype.tenancy_contract.tenancy_contract import make_sales_invoice, \
    validate_dates_before_invoice_gen
from property.property_management.doctype.property_management_settings.property_management_settings \
    import load_configuration

log = logger.get_logger(__name__)


def daily():
    today = nowdate()
    log.info("Begin rental invoice generation processing on %s", (today,))

    gen_date = load_configuration('automatic_invoice_generation_date', 26)
    if gen_date == 0:
        gen_date = 26

    d = getdate()
    if d.day != gen_date:
        log.info("Not generating invoices today. Current date is %s "
                 "while date of generation is configured as %s. Skipping...", today, gen_date)
        return

    contracts_active = frappe.get_list('Tenancy Contract', fields=['*'], filters={'contract_status': 'Active'})
    log.info("Loaded %s active contracts for processing", str(len(contracts_active)))

    # Remove those we don't have to bill yet...
    contracts_to_bill = []
    contracts_processed = {}
    contracts_failed = []
    log.info('Checking for valid first day of billing...')

    for c in contracts_active:
        log_identifier = 'Tenancy Contract id: {}, property unit name: {}, for Customer: {}'.format(c.name, c.property_unit_name, c.customer)
        tc_doc = frappe.get_doc("Tenancy Contract", c.name)
        try:
            validate_dates_before_invoice_gen(tc_doc)
            contracts_to_bill.append(c)
        except ValidationError:
            log.info("Not processing contract. First day of billing not yet reached: %s", log_identifier, exc_info=True)
        except:
            log.error("Error checking first day of billing validity for: %s", log_identifier, exc_info=True)
            contracts_failed.append(c)

    log.info("Found %s active contracts valid for billing...", str(len(contracts_to_bill)))

    for c in contracts_to_bill:
        log_identifier = 'Tenancy Contract id: {}, property unit name: {}, for Customer: {}'.format(c.name, c.property_unit_name, c.customer)
        log.info("Processing %s", log_identifier)
        try:
            invoice = make_sales_invoice(c.name)
            contracts_processed[c.name] = invoice
            frappe.db.commit()
            log.info('Successfully processed invoice for %s. The Invoice Number is: %s', log_identifier, invoice.name)
        except:
            log.error('Failed to process invoice for %s', log_identifier, exc_info=True)
            contracts_failed.append(c)
            frappe.db.rollback()

    # If the commit above did not happen, always roll back
    frappe.db.rollback()

    log.info("Finished processing Tenancy Contract invoices for date: %s", (today,))
    log.info("Total Active: %s", str(len(contracts_active)))
    log.info("Total To Invoice: %s", str(len(contracts_to_bill)))
    log.info("Total Invoiced: %s", str(len(contracts_processed)))
    log.info("Total Failed: %s", str(len(contracts_failed)))
