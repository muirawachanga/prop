# -*- coding: utf-8 -*-
# Copyright (c) 2015, Bituls Company Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import today, flt
from frappe.model.mapper import get_mapped_doc, _

class TenancyContract(Document):

	def validate(self):
		pass



@frappe.whitelist()
def get_item_details(item_code):
	item = frappe.db.sql("""select item_name, stock_uom, image, description, item_group, brand, income_account, selling_cost_center
		from `tabItem` where name = %s""", item_code, as_dict=1)
	return {
		'item_name': item and item[0]['item_name'] or '',
		'uom': item and item[0]['stock_uom'] or '',
		'description': item and item[0]['description'] or '',
		'image': item and item[0]['image'] or '',
		'item_group': item and item[0]['item_group'] or '',
		'brand': item and item[0]['brand'] or '',
		'income_account': item and item[0]['income_account'] or '',
		'cost_center': item and item[0]['selling_cost_center'] or ''
	}

@frappe.whitelist()
def generate_invoice(dn):
	"""
	Generate invoices for all property units based on the tenant contracts.
	"""
	contracts = frappe.db.sql("""select * from `tabTenancy Contract` where auto_generate_invoice = %(auto)s
							 and date_of_first_billing <= %(date)s and
							 status = %(status)s """, {"date": today(), "auto": 1, "status": "Active"}, as_dict=True)
	print contracts
	if not contracts:
		print "No tenant contracts to generate invoices for."
		return

	for c in contracts:
		invoice = __generate_invoice(c)
		if (c.email_invoice == 1):
			__send_email(invoice, c)

@frappe.whitelist()
def make_sales_invoice(source_name, target_doc=None, ignore_permissions=False):

	verify_items(source_name)

	def postprocess(source, target):
		set_missing_values(source, target)
		#Get the advance paid Journal Entries in Sales Invoice Advance
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

	doclist = get_mapped_doc("Tenancy Contract", source_name, {
		"Tenancy Contract": {
			"doctype": "Sales Invoice",
			"field_map": {
				"party_account_currency": "party_account_currency"
			},
			"validation": {
				"status": ["=", "Active"]
			}
		},
		"Tenancy Contract Item": {
			"doctype": "Sales Invoice Item",
			"postprocess": update_item
		}
	}, target_doc, postprocess, ignore_permissions=ignore_permissions)
	print doclist
	#doclist.submit()
	return doclist

def verify_items(name):
	tc = frappe.get_doc("Tenancy Contract", name)
	if not len(tc.items):
		frappe.msgprint(_('No Contract Items to invoice for this contract.'),raise_exception=1)
