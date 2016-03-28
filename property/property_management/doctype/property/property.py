# -*- coding: utf-8 -*-
# Copyright (c) 2015, Bituls Company Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Property(Document):
	def create_cost_center(self):
		cost_c = frappe.get_doc({"doctype": "Cost Center", "cost_center_name": self.property_name, "parent_cost_center": self.parent_cost_center,
								"company": self.company, "is_group": 0})
		cost_c = cost_c.insert()
		self.property_cost_center = cost_c.name
