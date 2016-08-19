# -*- coding: utf-8 -*-
# Copyright (c) 2015, Bituls Company Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe import db
from frappe.model.document import Document


class OwnerContract(Document):
    def validate(self):
        if db.get_value("Owner Contract", {"name": self.name}, "contract_status") in ["Cancelled", "Terminated",
                                                                                      "Rejected"]:
            frappe.throw(_('Cannot modify contracts in this status.'))
            # TODO Check if another active contract exists
