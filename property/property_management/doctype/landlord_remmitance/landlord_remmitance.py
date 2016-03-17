# -*- coding: utf-8 -*-
# Copyright (c) 2015, Bituls Company Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint, _
from frappe.utils import today

class LandlordRemmitance(Document):
	def get_details(self):
		if not (self.owner_contract):
			msgprint(_("Owner Contract is mandatory and should be selected."))
			return

		dl = frappe.db.sql("""select ti.* from `tabSales Invoice` ti, `tabOwner Contract` td, `tabProperty` tp, `tabProperty Unit` tu,
						`tabTenancy Contract` tc where ti.tenancy_contract = tc.name and tc.property_unit = tu.name
						and tu.property = tp.name and td.property = tp.name and td.name = '%s';""" %(self.owner_contract,), as_dict=1)

		for d in dl:
			nl = self.append('remittance_details', {})
			nl.invoice = d.name
			nl.tenancy_contract = d.tenancy_contract
			nl.invoice_date = d.posting_date
			nl.invoice_status = 'Paid' if d.paid_amount else 'Pending'
			nl.invoice_payment_date = today()
			nl.total = d.net_total
			nl.grand_total = d.total
			nl.taxes_and_charges = d.total_taxes_and_charges
