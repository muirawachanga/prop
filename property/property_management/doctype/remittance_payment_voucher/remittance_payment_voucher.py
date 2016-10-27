# -*- coding: utf-8 -*-
# Copyright (c) 2015, Bituls Company Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from erpnext.accounts.party import get_party_account
from frappe import _
from frappe.exceptions import ValidationError
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt

'''
*Create new remittance payment voucher
*User enters a payment method. Cash - Cash Acct. Bank - Select Bank Accout
*Create Journal Entry for the remittance amt payment. Acct selected above vs the trust fund account for this property.
*Create advance payment JV for the management fees and deductibles.
*Create invoice for deductible expenses to Landlord.
*Create invoice for management fees to landlord.
*Invoices created above are reconciled with the credits made to landlord account. This is automatic via
*get_advance call on the invoice.
*Finally display a button on this document for viewing all the rest. 'Highlight' it after everything is done.
'''


class RemittancePaymentVoucher(Document):
    def get_customer_name(self):
        owc = frappe.get_doc('Owner Contract', self.get('owner_contract'))
        return owc.owner_customer

    def on_submit(self):
        self.set('user_remark',
                 self.get('user_remark') or "" + " Being Remittance Payment for Landlord Remittance No: " +
                 self.get("landlord_remittance"))

        def postprocess(source, target):
            voucher_type = "Cash Entry" if source.get("payment_method") == "Cash" else "Bank Entry"
            target.set("voucher_type", voucher_type)

            cr_entry = target.append("accounts", {})
            cr_entry.account = source.get("payment_account")
            cr_entry.credit_in_account_currency = source.get("amount_paid")

            dr_entry = target.append("accounts", {})
            dr_entry.account = source.get("trust_fund_account")
            dr_entry.debit_in_account_currency = source.get("amount_paid")
            dr_entry.reference_type = 'Remittance Payment Voucher'
            dr_entry.reference_name = self.name

            target.set("posting_date", source.get("posting_date"))
            target.set("user_remark", target.get('user_remark') or "" +
                       " Being Remittance Payment for Landlord Remittance No: " + source.get("landlord_remittance"))
            target.flags.ignore_permissions = True

        journal_e = get_mapped_doc(self.doctype, self.name, {
            "Remittance Payment Voucher": {
                "doctype": "Journal Entry",
                "field_map": {
                    "reference_number": "cheque_no",
                    "reference_date": "cheque_date",
                },
            }
        }, None, postprocess)
        journal_e.submit()

        lr = frappe.get_doc('Landlord Remittance', self.landlord_remittance)
        lr.set('payment_status', 'Settled')
        lr.db_update()
        # Create advances into landlord's customer account from the trust fund account.
        # This will be used to pay the commissions and expense deduction invoices
        adv_journal_entry = self.create_advance()

        # Create the invoices to landlord
        self.create_management_fee_invoice(adv_journal_entry)
        self.create_deductions_invoice(adv_journal_entry)

    def before_cancel(self):
        mgt_fee_inv = frappe.get_list("Sales Invoice", fields="*", filters=[["remittance_reference", "=", self.name],
                                                                            ["docstatus", "=", 1]])
        for i in mgt_fee_inv:
            inv = frappe.get_doc('Sales Invoice', i.get('name'))
            inv.flags.ignore_permissions = True
            inv.cancel()

        jea = frappe.get_list("Journal Entry Account", fields="*", filters=[["reference_name", "=", self.name],
                                                                            ["docstatus", "=", 1]])
        for j in jea:
            je = frappe.get_doc('Journal Entry', j.get('parent'))
            je.flags.ignore_permissions = True
            je.cancel()

    def on_cancel(self):
        lr = frappe.get_doc('Landlord Remittance', self.landlord_remittance)
        lr.set('payment_status', 'Pending')
        lr.db_update()

    def validate(self):
        lr = frappe.get_doc("Landlord Remittance", self.landlord_remittance)

        if lr.docstatus != 1:
            raise ValidationError("Landlord Remittance must be submitted first before payment.")

        if lr.payment_status == 'Settled':
            raise ValidationError("Remittance already settled. Cannot create a Remittance Voucher.")

        if self.amount_paid <= 0:
            frappe.throw("Amount Paid is invalid. Cannot be zero or less.")

        if self.net_remittance_amount <= 0:
            frappe.throw("Net Remittance amount is invalid. Cannot be zero or less.")

        if self.management_fee < 0:
            frappe.throw("Management Fee amount is invalid. Cannot be less than zero.")

        if self.deductible_expenses < 0:
            frappe.throw("Deductible Expenses amount is invalid. Cannot be less than zero.")

    def create_deductions_invoice(self, adv_journal_entry):
        if self.get("deductible_expenses") == 0:
            return
        inv = frappe.new_doc('Sales Invoice')
        cust = frappe.get_doc('Customer', self.get_customer_name())
        inv.set("customer", cust.name, True)
        # inv.set('title', cust.name)
        inv_items = frappe.new_doc('Sales Invoice Item')

        settings = frappe.get_single("Property Management Settings")
        if settings.default_expense_reimbursement_item in (None, ""):
            frappe.throw(_("Invoice item for expense reimbursement fee items is missing. "
                           "Please set it under Property Management Settings."))

        inv_items.set("item_code", settings.default_expense_reimbursement_item)
        inv_items.set("item_name", settings.default_expense_reimbursement_item)
        inv_items.set("description", settings.default_expense_reimbursement_item)
        inv_items.set("qty", 1.0)
        inv_items.set("rate", self.deductible_expenses)
        inv.set("items", [inv_items])

        inv.is_pos = 0
        inv.ignore_pricing_rule = 1
        inv.flags.ignore_permissions = True
        inv.run_method("set_missing_values")
        inv.run_method("calculate_taxes_and_totals")

        self.alloc_advances(inv, adv_journal_entry)

        inv.set('remittance_reference', self.name)
        inv.save()
        inv.submit()

    def create_management_fee_invoice(self, adv_journal_entry):
        if self.get("management_fee") == 0:
            return
        inv = frappe.new_doc('Sales Invoice')
        cust = frappe.get_doc('Customer', self.get_customer_name())
        inv.set("customer", cust.name, True)
        # inv.set('title', cust.name)
        inv_items = frappe.new_doc('Sales Invoice Item')
        settings = frappe.get_single("Property Management Settings")
        if settings.default_management_fee_item in (None, ""):
            frappe.throw(_("Invoice item for management fee items is missing. "
                           "Please set it under Property Management Settings."))
        inv_items.set("item_code", settings.default_management_fee_item)
        inv_items.set("item_name", settings.default_management_fee_item)
        inv_items.set("description", settings.default_management_fee_item)
        inv_items.set("qty", 1.0)
        inv_items.set("rate", self.management_fee)
        inv.set("items", [inv_items])

        inv.is_pos = 0
        inv.ignore_pricing_rule = 1
        inv.flags.ignore_permissions = True
        inv.run_method("set_missing_values")
        inv.run_method("calculate_taxes_and_totals")

        self.alloc_advances(inv, adv_journal_entry)

        inv.set('remittance_reference', self.name)
        inv.save()
        inv.submit()

    def alloc_advances(self, inv, adv_je):
        inv.run_method("set_advances")
        # set_advance call above does not allocate if we have no sales order
        # linked to the Advance Journal Entry. So we do it now... we want the advance coming from the advance
        # payment journal we just made
        adv = next((ad for ad in inv.get('advances') if ad.get('reference_name') == adv_je.name), None)
        if not adv:
            frappe.throw(_("Advance Payment allocation error during Remittance Payment processing. "
                           "Please contact support."))
        adv.set('allocated_amount', flt(inv.get('grand_total')))
        return adv

    def create_advance(self):
        journal_entry = frappe.new_doc('Journal Entry')
        journal_amt = flt(self.get("management_fee") + self.get('deductible_expenses'))
        if journal_amt == 0:
            return
        cr_entry = journal_entry.append("accounts", {})
        cr_entry.account = get_party_account('Customer', self.get_customer_name(), journal_entry.company)
        cr_entry.credit_in_account_currency = journal_amt
        cr_entry.party_type = 'Customer'
        cr_entry.party = self.get_customer_name()
        cr_entry.is_advance = 'Yes'

        dr_entry = journal_entry.append("accounts", {})
        dr_entry.account = self.get("trust_fund_account")
        dr_entry.debit_in_account_currency = journal_amt
        dr_entry.reference_type = 'Remittance Payment Voucher'
        dr_entry.reference_name = self.name
        journal_entry.set("posting_date", self.get("posting_date"))
        journal_entry.set("user_remark", journal_entry.get('user_remark') or "" +
                          " Being management fee / Reimbursed Expenses settlement for Landlord Remittance No: " + self.get(
            "landlord_remittance"))
        journal_entry.flags.ignore_permissions = True
        journal_entry.save()
        journal_entry.submit()
        return journal_entry
