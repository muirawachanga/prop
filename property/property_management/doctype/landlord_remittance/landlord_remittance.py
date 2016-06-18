# -*- coding: utf-8 -*-
# Copyright (c) 2015, Bituls Company Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe import msgprint, _, throw

class LandlordRemittance(Document):

	def get_remit_flags(self,item, tc):
		tc_item = frappe.db.sql("""select * from `tabTenancy Contract Item` tci where item_code = '%s' and parent = '%s';
								""" %(item.item_code, tc), as_dict=1)
		if not len(tc_item):
			#This item is not in the Tenancy Contract. No remitting.
			return (False, False)

		return (True if tc_item[0].remmitable else False, True if tc_item[0].remit_full_amount else False,)

	def get_collections(self, invoices):
		self.set('collection_invoices', [])
		self.set('collections_details', [])
		total_collections = flt(0)
		remittable_collections = flt(0)
		for inv in invoices:
			ci = self.append('collection_invoices', {})
			ci.invoice = inv.invoice_name
			ci.tenant_name = inv.customer
			ci.invoice_date = inv.posting_date
			ci.property_name = inv.property_name
			ci.property_unit_name = inv.unit_name
			ci.tenancy_contract = inv.contract_name
			ci.grand_total = inv.grand_total
			ci.remittance_amount = inv.grand_total
			inv_items = frappe.db.sql("""select tsi.* from `tabSales Invoice Item` tsi
											where tsi.parent = '%s';""" %(inv.invoice_name), as_dict=1)

			for it in inv_items:
				nl = self.append('collections_details', {})
				nl.invoice = inv.invoice_name
				nl.tenant_name = inv.customer
				nl.item_name = it.item_name
				nl.invoice_date = inv.posting_date
				nl.item_total = it.amount
				nl.is_remittable = 1
				nl.remit_full_amount = 0
				r_flags = self.get_remit_flags(it, inv.contract_name)
				if not r_flags[0]:
					#Remove this amount from the invoice total to remit
					ci.remittance_amount = ci.remittance_amount - it.amount
					nl.is_remittable = 0
				if r_flags[1]:
					nl.remit_full_amount = 1

			remittable_collections = flt(remittable_collections) + flt(ci.remittance_amount)
			total_collections = flt(total_collections) + flt(ci.grand_total)

		self.set("total_collections", total_collections)
		self.set("remittable_collections", remittable_collections)

	def get_expenses(self, invoices):
		self.set('expense_invoices', [])
		self.set('expense_details', [])
		total_expenses = flt(0)
		deductible_expenses = flt(0)
		for inv in invoices:
			ci = self.append('expense_invoices', {})
			ci.invoice = inv.invoice_name
			ci.supplier_name = inv.supplier_name
			ci.invoice_date = inv.posting_date
			ci.grand_total = inv.grand_total
			ci.deduction_amount = inv.grand_total

			inv_items = frappe.db.sql("""select tpi.* from `tabPurchase Invoice Item` tpi
											where tpi.parent = '%s';""" %(inv.invoice_name), as_dict=1)

			for it in inv_items:
				nl = self.append('expense_details', {})
				nl.invoice = inv.invoice_name
				nl.supplier_name = inv.supplier_name
				nl.item_name = it.item_name
				nl.invoice_date = inv.posting_date
				nl.item_total = it.amount
				nl.is_deductible = 1
				if it.not_landlord_expense:
					#Remove this amount from the invoice total to deduct
					ci.deduction_amount = ci.deduction_amount - it.amount
					nl.is_deductible = 0

			deductible_expenses = flt(deductible_expenses) + flt(ci.deduction_amount)
			total_expenses = flt(total_expenses) + flt(ci.grand_total)

		self.set("total_expenses", total_expenses)
		self.set("deductible_expenses", deductible_expenses)

	def load_commission_rate(self):
		if not self.commission_rate:
			self.commission_rate = frappe.db.get_value('Owner Contract', self.owner_contract, 'commision')

	def load_remittance_summary(self, desc, amount):
		if not self.get('remittance_summary'):
			self.set('remittance_summary', [])
		#If description already exists, just update the amount.
		ex = [e for e in self.get('remittance_summary') if e.description == desc]
		if ex:
			ex[0].amount = amount
			return
		summary = self.append('remittance_summary', {})
		summary.description = desc
		summary.amount = amount

	def calculate_commision(self):
		base_amount = flt(0)

		for r in self.collections_details:
			if r.remit_full_amount:
				continue
			if not r.is_remittable:
				continue
			base_amount = flt(base_amount) + flt(r.item_total)

		self.load_commission_rate()
		commission_amount = flt(base_amount) * (flt(self.commission_rate) / flt(100))
		self.management_fee = commission_amount
		self.remittance_amount = flt(self.remittable_collections) - (flt(commission_amount) + flt(self.deductible_expenses))

		self.load_remittance_summary('Total Collections', self.total_collections)
		self.load_remittance_summary('Remittable Collections', self.remittable_collections)
		self.load_remittance_summary('Commission Exempted Collections', flt(self.remittable_collections) - flt(base_amount))
		self.load_remittance_summary('Commission Eligible Collections', base_amount)
		self.load_remittance_summary('Commission Charged', commission_amount)
		self.load_remittance_summary('Total Expenses', self.total_expenses)
		self.load_remittance_summary('Deductible Expenses', self.deductible_expenses)
		self.load_remittance_summary('Net Amount To Landlord', self.remittable_collections - (flt(commission_amount) + flt(self.deductible_expenses)))



	def get_details(self):
		if not (self.owner_contract):
			msgprint(_("Owner Contract is mandatory and should be selected."))
			return
		#Get all invoices that have been generated but not already been remitted
		inv_query = """select ti.name as invoice_name, tp.property_name, tu.unit_name, tc.customer,
											tc.name as contract_name, ti.posting_date, ti.outstanding_amount, ti.grand_total from
											`tabSales Invoice` ti, `tabOwner Contract` td, `tabProperty` tp, `tabProperty Unit` tu,
											`tabTenancy Contract` tc where ti.docstatus = 1 and ti.tenancy_contract = tc.name and tc.property_unit = tu.name
											and tu.property = tp.name and td.property = tp.name and td.name = '%s' and ti.posting_date between '%s' and '%s'
											and ti.name not in
											(select lc.invoice from `tabLandlord Collection Invoices` lc, `tabLandlord Remittance` lr where lr.owner_contract = '%s'
											and lr.name = lc.parent and lc.docstatus <> 2)
											order by tc.customer, ti.posting_date;
											""" %(self.owner_contract, self.period_start, self.period_end, self.owner_contract)

		if self.exclude_unpaid_invoices:
			inv_query = """select ti.name as invoice_name, tp.property_name, tu.unit_name, tc.customer,
											tc.name as contract_name, ti.posting_date, ti.outstanding_amount, ti.grand_total from
											`tabSales Invoice` ti, `tabOwner Contract` td, `tabProperty` tp, `tabProperty Unit` tu,
											`tabTenancy Contract` tc where ti.docstatus = 1 and ti.tenancy_contract = tc.name and tc.property_unit = tu.name
											and tu.property = tp.name and td.property = tp.name and td.name = '%s' and ti.posting_date between '%s' and '%s'
											and ti.name not in
											(select lc.invoice from `tabLandlord Collection Invoices` lc, `tabLandlord Remittance` lr where lr.owner_contract = '%s'
											and lr.name = lc.parent and lc.docstatus <> 2) and ti.outstanding_amount = 0
											order by tc.customer, ti.posting_date;
											""" %(self.owner_contract,  self.period_start, self.period_end, self.owner_contract)

		collection_invoices = frappe.db.sql(inv_query, as_dict=1)

		if not len(collection_invoices):
			msgprint(_("There are no invoices pending remittance for the selected contract."))
			return

		self.get_collections(collection_invoices)

		expense_invoices = frappe.db.sql("""select ti.name as invoice_name, ti.posting_date, ti.grand_total, ti.supplier_name from
											`tabPurchase Invoice` ti, `tabOwner Contract` td, `tabProperty` tp where ti.owner_contract = td.name and
											td.property = tp.name and td.name = '%s' and ti.name not in
											(select lei.invoice from `tabLandlord Expense Invoices` lei, `tabLandlord Remittance` lr
											where lr.owner_contract = '%s' and lr.name = lei.parent);
											""" %(self.owner_contract, self.owner_contract), as_dict=1)

		if len(expense_invoices):
			self.get_expenses(expense_invoices)

		self.calculate_commision()
