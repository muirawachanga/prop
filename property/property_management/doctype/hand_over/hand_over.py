# -*- coding: utf-8 -*-
# Copyright (c) 2019, Bituls Company Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.desk.reportview import get_match_cond

class HandOver(Document):
	pass

@frappe.whitelist()
def tenancy_contract_query(doctype, txt, searchfield, start, page_len, filters):
	# Select only property units that don't have Tenancy Contracts that are in specific statuses.
	# Specify these filters in filters["tc_filters"]. e.g:
	# Specify the 'side' (IN or NOT IN) using filters["side"]
	property_filter = ""
	if filters.get("property_name"):
		property_filter = "and property_name = %s"
	prop = [] if not filters.get("property_name") else [filters.get("property_name")]

	return frappe.db.sql("select name, property_unit_name from `tabTenancy Contract` where contract_status='Terminated' and name {side} "
						 "(select tenancy_contract from `tabHand Over` where status in "
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
