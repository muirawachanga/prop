# -*- coding: utf-8 -*-
# Copyright (c) 2015, Bituls Company Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _, DoesNotExistError
from frappe import db

class OwnerContract(Document):

	def validate(self):

		if db.get_value("Owner Contract", {"name": self.name}, "status") in ["Cancelled", "Terminated"]:
			frappe.throw(_('Cannot modify contracts in this status.'))
