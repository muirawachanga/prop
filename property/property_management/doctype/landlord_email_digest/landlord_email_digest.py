# -*- coding: utf-8 -*-
# Copyright (c) 2018, Bituls Company Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cstr
from frappe.desk.reportview import get_match_cond
from frappe.model.document import Document
from frappe.utils import fmt_money, formatdate, format_time, now_datetime, \
	get_url_to_form, get_url_to_list, flt, nowdate
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from frappe.core.doctype.user.user import STANDARD_USERS
import frappe.desk.notifications
from erpnext.accounts.utils import get_fiscal_year

class LandlordEmailDigest(Document):
	def autoname(self):
		# group name and id
		self.name = "-".join(filter(None,
									[cstr(self.get(f)).strip() for f in ["landlord", "property_name"]]))
	def __init__(self, *args, **kwargs):
		super(LandlordEmailDigest, self).__init__(*args, **kwargs)
		self.from_date, self.to_date = self.get_from_to_date()
		self.set_dates()
		self._accounts = {}
		self.company = frappe.defaults.get_global_default("company")
		self.currency = frappe.db.get_value("Company", self.company, "default_currency")

	def send(self, user_doc):
		# send email only to enabled users
		valid_doc = [p[0] for p in frappe.db.sql("""select name from `tabLandlord Email Digest`
			where enabled=1 and docstatus<2""")]
		if valid_doc:
			# TODO make sure to implement a asynchronous function
			doc = frappe.get_doc("Landlord Email Digest", user_doc)
			msg_for_this_receipient = doc.get_msg_html()
			if msg_for_this_receipient:
				frappe.sendmail(
					recipients=doc.email,
					subject=_("{frequency} Digest").format(frequency=self.frequency),
					message=msg_for_this_receipient,
					reference_doctype = self.doctype,
					reference_name = self.name,
					unsubscribe_message = _("Unsubscribe from this Email Digest"))
				# should update the note after sending the mail.
				self.reset_note()


	def get_msg_html(self):
		"""Build email digest content"""
		frappe.flags.ignore_account_permission = True
		from property.property_management.doctype.landlord_email_digest.quotes import get_random_quote

		context = frappe._dict()
		context.update(self.__dict__)

		self.set_title(context)
		self.set_style(context)
		self.set_accounting_cards(context)
		if self.get("note"):
			context.notifications = self.get_note()
		quote = get_random_quote()
		context.quote = {"text": quote[0], "author": quote[1]}

		if not context.cards:
			return None

		frappe.flags.ignore_account_permission = False
		# self.reset_fields(context)

		# style
		return frappe.render_template("property/property_management/doctype/landlord_email_digest/templates/default.html",
									  context, is_path=True)


	def set_title(self, context):
		"""Set digest title"""
		if self.frequency=="Daily":
			context.title = _("Daily Reminders")
			context.subtitle = _("Pending activities for today")
		elif self.frequency=="Weekly":
			context.title = _("This Week's Summary")
			context.subtitle = _("Summary for this week and pending activities")
		elif self.frequency=="Monthly":
			context.title = _("This Month's Summary")
			context.subtitle = _("Summary for this month and pending activities")

	def set_style(self, context):
		"""Set standard digest style"""
		context.text_muted = '#8D99A6'
		context.text_color = '#36414C'
		context.h1 = 'margin-bottom: 30px; margin-top: 40px; font-weight: 400; font-size: 30px;'
		context.h2 = 'margin-bottom: 30px; margin-top: -20px; font-weight: 400; font-size: 20px;'
		context.label_css = '''display: inline-block; color: {text_muted};
			padding: 3px 7px; margin-right: 7px;'''.format(text_muted = context.text_muted)
		context.section_head = 'margin-top: 60px; font-size: 16px;'
		context.line_item  = 'padding: 5px 0px; margin: 0; border-bottom: 1px solid #d1d8dd;'
		context.link_css = 'color: {text_color}; text-decoration: none;'.format(text_color = context.text_color)

	def get_from_to_date(self):
		today = now_datetime().date()

		# decide from date based on email digest frequency
		if self.frequency == "Daily":
			# from date, to_date is yesterday
			from_date = to_date = today - timedelta(days=1)
		elif self.frequency == "Weekly":
			# from date is the previous week's monday
			from_date = today - timedelta(days=today.weekday(), weeks=1)

			# to date is sunday i.e. the previous day
			to_date = from_date + timedelta(days=6)
		else:
			# from date is the 1st day of the previous month
			from_date = today - relativedelta(days=today.day-1, months=1)
			# to date is the last day of the previous month
			to_date = today - relativedelta(days=today.day)

		return from_date, to_date

	def set_dates(self):
		self.future_from_date, self.future_to_date = self.from_date, self.to_date

		# decide from date based on email digest frequency
		if self.frequency == "Daily":
			self.past_from_date = self.past_to_date = self.future_from_date - relativedelta(days = 1)

		elif self.frequency == "Weekly":
			self.past_from_date = self.future_from_date - relativedelta(weeks=1)
			self.past_to_date = self.future_from_date - relativedelta(days=1)
		else:
			self.past_from_date = self.future_from_date - relativedelta(months=1)
			self.past_to_date = self.future_from_date - relativedelta(days=1)

	def get_next_sending(self):
		from_date, to_date = self.get_from_to_date()

		send_date = to_date + timedelta(days=1)

		if self.frequency == "Daily":
			next_send_date = send_date + timedelta(days=1)
		elif self.frequency == "Weekly":
			next_send_date = send_date + timedelta(weeks=1)
		else:
			next_send_date = send_date + relativedelta(months=1)
		self.next_send = formatdate(next_send_date) + " at midnight"

		return send_date

	def onload(self):
		self.get_next_sending()

	def get_collections(self, invoices):
		total_collections = flt(0)
		remittable_collections = flt(0)
		for inv in invoices:
			grand_total = inv.grand_total
			remittance_amount = inv.grand_total
			inv_items = frappe.db.sql("""select tsi.* from `tabSales Invoice Item` tsi
												where tsi.parent = '%s';""" % (inv.invoice_name), as_dict=1)

			for it in inv_items:
				is_remittable = it.remittable
				print(is_remittable)
				if not is_remittable:
					# Remove this amount from the invoice total to remit
					remittance_amount = remittance_amount - it.amount

			remittable_collections = flt(remittable_collections) + flt(remittance_amount)
			total_collections = flt(total_collections) + flt(grand_total)
		return remittable_collections


	def get_expenses(self, invoices):
		total_expenses = flt(0)
		deductible_expenses = flt(0)
		for inv in invoices:
			grand_total = inv.grand_total
			deduction_amount = inv.grand_total

			inv_items = frappe.db.sql("""select tpi.* from `tabPurchase Invoice Item` tpi
												where tpi.parent = '%s';""" % (inv.invoice_name), as_dict=1)

			for it in inv_items:
				if it.not_landlord_expense:
					# Remove this amount from the invoice total to deduct
					deduction_amount = deduction_amount - it.amount

			deductible_expenses = flt(deductible_expenses) + flt(deduction_amount)
			total_expenses = flt(total_expenses) + flt(grand_total)
		return deductible_expenses


	def load_commission_rate(self):
		self.commission_rate = frappe.db.get_value('Owner Contract', self.landlord, 'commision')


	def reset_fields(self, context):
		context.notifications = []

	def set_accounting_cards(self, context):
		"""Create accounting cards if checked"""
		cache = {}
		context.cards = []
		for key in ("ann_total_collection","ann_expected_income","ann_total_expenses", "ann_total_fees","total_collection", "expected_income", "total_expenses", "total_fees", "total_occupied", "total_unoccupied"):
			if self.get(key):
				cache_key = "email_digest:card:{0}:{1}:{2}:{3}".format(self.name, self.frequency, key, self.from_date)
				card = cache.get(cache_key)

				if card:
					card = eval(card)

				else:
					card = frappe._dict(getattr(self, "get_" + key)())
					if key == "total_occupied":
						pass
					elif key == "total_unoccupied":
						pass
					else:
						card.value = self.fmt_money(card.value, False)
					# cache.setex(cache_key, card, 24 * 60 * 60)

				context.cards.append(card)
		frappe.clear_cache()

	def get_total_collection(self):
		# This includes unpaid invoices as well
		inv_query = """select ti.name as invoice_name, tp.property_name, tu.unit_name, tc.customer,
												tc.name as contract_name, ti.posting_date, ti.outstanding_amount, ti.grand_total from
												`tabSales Invoice` ti, `tabOwner Contract` td, `tabProperty` tp, `tabProperty Unit` tu,
												`tabTenancy Contract` tc where ti.docstatus = 1 and ti.tenancy_contract = tc.name and tc.property_unit = tu.name
												and tu.property = tp.name and td.property = tp.name and td.name = '%s' and ti.posting_date between '%s' and '%s'
												and ti.name not in
												(select lc.invoice from `tabLandlord Collection Invoices` lc, `tabLandlord Remittance` lr where lr.owner_contract = '%s'
												and lr.name = lc.parent and lc.docstatus <> 2)
												order by tc.customer, ti.posting_date;
												""" % (
			self.landlord, self.from_date, self.to_date, self.landlord)
		collection_invoices = frappe.db.sql(inv_query, as_dict=1)

		if len(collection_invoices):
			amount = self.get_collections(collection_invoices)
			return {
				"label": self.meta.get_label("total_collection"),
				"value": amount
			}
		if not len(collection_invoices):
			return {
				"label": self.meta.get_label("total_collection"),
				"value": 0.00
			}
	def get_expected_income(self):
		revenue = frappe._dict(self.get_total_collection())
		total_revenue = revenue.value
		expenses = frappe._dict(self.get_total_expenses())
		total_expenses = expenses.value
		management_fee = frappe._dict(self.get_total_fees())
		management_fees = management_fee.value
		total_income = total_revenue - (total_expenses + management_fees)
		return {
			"label": self.meta.get_label("expected_income"),
			"value": total_income
		}
	def get_total_expenses(self):
		expense_invoice = frappe.db.sql("""select ti.name as invoice_name, ti.posting_date, ti.grand_total, ti.supplier_name from
											`tabPurchase Invoice` ti, `tabOwner Contract` td, `tabProperty` tp where ti.owner_contract = td.name and
											td.property = tp.name and td.name = '%s' and ti.posting_date between '%s' and '%s' and ti.docstatus = 1 and ti.name not in
											(select lei.invoice from `tabLandlord Expense Invoices` lei, `tabLandlord Remittance` lr
											where lr.owner_contract = '%s' and lr.name = lei.parent and lei.docstatus <> 2)
											order by ti.supplier_name, ti.posting_date;
											""" % (
			self.landlord, self.from_date, self.to_date, self.landlord), as_dict=1)
		if len(expense_invoice):
			amount = self.get_expenses(expense_invoice)
			return {
				"label": self.meta.get_label("total_expenses"),
				"value": amount
			}
		if not len(expense_invoice):
			return {
				"label": self.meta.get_label("total_expenses"),
				"value": 0.00
			}

	def get_total_fees(self):
		self.load_commission_rate()
		self.management_fee = 0.00
		revenue = frappe._dict(self.get_total_collection())
		total_revenue = revenue.value
		self.management_fee = flt(total_revenue) * (flt(self.commission_rate) / flt(100))
		return {
			"label": self.meta.get_label("total_fees"),
			"value": self.management_fee
		}
	# TODO get a better way to write the fuction instead of the repetition

	def get_ann_total_collection(self):
		# This includes unpaid invoices as well
		inv_query = """select ti.name as invoice_name, tp.property_name, tu.unit_name, tc.customer,
												tc.name as contract_name, ti.posting_date, ti.outstanding_amount, ti.grand_total from
												`tabSales Invoice` ti, `tabOwner Contract` td, `tabProperty` tp, `tabProperty Unit` tu,
												`tabTenancy Contract` tc where ti.docstatus = 1 and ti.tenancy_contract = tc.name and tc.property_unit = tu.name
												and tu.property = tp.name and td.property = tp.name and td.name = '%s' and ti.posting_date between '%s' and '%s'
												and ti.name not in
												(select lc.invoice from `tabLandlord Collection Invoices` lc, `tabLandlord Remittance` lr where lr.owner_contract = '%s'
												and lr.name = lc.parent and lc.docstatus <> 2)
												order by tc.customer, ti.posting_date;
												""" % (
			self.landlord, year_start_date(), self.to_date, self.landlord)
		collection_invoices = frappe.db.sql(inv_query, as_dict=1)

		if len(collection_invoices):
			amount = self.get_collections(collection_invoices)
			return {
				"label": self.meta.get_label("ann_total_collection"),
				"value": amount
			}
		if not len(collection_invoices):
			return {
				"label": self.meta.get_label("ann_total_collection"),
				"value": 0.00
			}
	def get_ann_expected_income(self):
		revenue = frappe._dict(self.get_ann_total_collection())
		total_revenue = revenue.value
		expenses = frappe._dict(self.get_ann_total_expenses())
		total_expenses = expenses.value
		management_fee = frappe._dict(self.get_ann_total_fees())
		management_fees = management_fee.value
		total_income = total_revenue - (total_expenses + management_fees)
		return {
			"label": self.meta.get_label("ann_expected_income"),
			"value": total_income
		}
	def get_ann_total_expenses(self):
		expense_invoice = frappe.db.sql("""select ti.name as invoice_name, ti.posting_date, ti.grand_total, ti.supplier_name from
											`tabPurchase Invoice` ti, `tabOwner Contract` td, `tabProperty` tp where ti.owner_contract = td.name and
											td.property = tp.name and td.name = '%s' and ti.posting_date between '%s' and '%s' and ti.docstatus = 1 and ti.name not in
											(select lei.invoice from `tabLandlord Expense Invoices` lei, `tabLandlord Remittance` lr
											where lr.owner_contract = '%s' and lr.name = lei.parent and lei.docstatus <> 2)
											order by ti.supplier_name, ti.posting_date;
											""" % (
			self.landlord, year_start_date(), self.to_date, self.landlord), as_dict=1)
		if len(expense_invoice):
			amount = self.get_ann_expenses(expense_invoice)
			return {
				"label": self.meta.get_label("ann_total_expenses"),
				"value": amount
			}
		if not len(expense_invoice):
			return {
				"label": self.meta.get_label("ann_total_expenses"),
				"value": 0.00
			}

	def get_ann_total_fees(self):
		self.load_commission_rate()
		self.management_fee = 0.00
		revenue = frappe._dict(self.get_ann_total_collection())
		total_revenue = revenue.value
		self.management_fee = flt(total_revenue) * (flt(self.commission_rate) / flt(100))
		return {
			"label": self.meta.get_label("ann_total_fees"),
			"value": self.management_fee
		}
	def get_total_occupied(self):
		active = frappe.db.sql("""select count(*) from `tabOwner Contract` td, `tabProperty` tp, `tabProperty Unit` tu, `tabTenancy Contract` tc where
									tu.property = tp.name and td.property = tp.name and td.name = '%s' and tc.property_unit = tu.name
									and tc.contract_status = 'Active';""" % (self.landlord,), as_dict=0)
		value = int(active[0][0])
		return {
			"label": self.meta.get_label("total_occupied"),
			"value": value
		}

	def get_total_unoccupied(self):
		all = frappe.db.sql("""select count(*) from `tabOwner Contract` td, `tabProperty` tp, `tabProperty Unit` tu where
								tu.property = tp.name and td.property = tp.name and td.name = '%s';
								""" % (self.landlord,), as_dict=0)
		occupied = frappe._dict(self.get_total_occupied())
		active = int(occupied.value)
		unoccupied = int(all[0][0]) - active
		return {
			"label": self.meta.get_label("total_unoccupied"),
			"value": unoccupied
		}
	def get_note(self):
		return self.note

	def reset_note(self):
		frappe.db.sql("""update `tabLandlord Email Digest` set note = '' where name='%s'""" %self.name)

	def fmt_money(self, value, absol=True):
		if absol:
			return fmt_money(abs(value), currency = self.currency)
		else:
			return fmt_money(value, currency=self.currency)
def send():
	now_date = now_datetime().date()
	for ed in frappe.db.sql("""select name from `tabLandlord Email Digest`
			where enabled=1 and docstatus<2""", as_list=1):
		ed_obj = frappe.get_doc('Landlord Email Digest', ed[0])
		if (now_date == ed_obj.get_next_sending()):
			ed_obj.send(ed[0])

@frappe.whitelist()
def landlord_query(doctype, txt, searchfield, start, page_len, filters):
	# Select only property units that don't have Tenancy Contracts that are in specific statuses.
	# Specify these filters in filters["tc_filters"]. e.g:
	# Specify the 'side' (IN or NOT IN) using filters["side"]
	property_filter = ""
	if filters.get("property_name"):
		property_filter = "and property_name = %s"
	prop = [] if not filters.get("property_name") else [filters.get("property_name")]

	return frappe.db.sql("select name, property_name from `tabOwner Contract` where contract_status='Active' and name {side} "
						 "(select landlord from `tabLandlord Email Digest` where enabled in "
						 "({statuses})) and ({key} like %s or property_name like %s) {prop} {mcond} "
						 "order by if(locate(%s, name), locate(%s, name), 99999), "
						 "if(locate(%s, property_name), locate(%s, property_name), 99999), "
						 "idx desc, name, property_name limit %s, %s".format(**{
		'key': searchfield,
		'mcond': get_match_cond(doctype),
		'side': filters["side"],
		'prop': property_filter,
		'statuses': ','.join(['%s'] * len(filters["tc_filters"]))
	}), filters["tc_filters"] + ["%%%s%%" % txt, "%%%s%%" % txt] + prop + [txt.replace("%", ""),
																		   txt.replace("%", ""),
																		   txt.replace("%", ""),
																		   txt.replace("%", ""),
																		   start, page_len])

@frappe.whitelist()
def get_digest_msg(name):
	return frappe.get_doc("Landlord Email Digest", name).get_msg_html()


def year_start_date():
	date = nowdate()
	year_start_dates = get_fiscal_year(date, verbose=0)[1]
	return year_start_dates


