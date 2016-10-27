# -*- coding: utf-8 -*-
# Copyright (c) 2016, Bituls Company Limited and contributors
# For license information, please see license.txt

from property.property_management.utils import disable_quick_entry
import frappe


def execute():
    disable_quick_entry('Item')
    frappe.db.commit()
