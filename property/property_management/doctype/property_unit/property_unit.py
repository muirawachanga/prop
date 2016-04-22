# -*- coding: utf-8 -*-
# Copyright (c) 2015, Bituls Company Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PropertyUnit(Document):
	def validate(self):
		combo_name = self.property_name + ' - ' + self.unit_name
		self.unit_name = combo_name
