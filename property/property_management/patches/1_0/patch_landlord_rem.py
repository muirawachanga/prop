# -*- coding: utf-8 -*-
# Copyright (c) 2015, Bituls Company Limited and contributors
# For license information, please see license.txt

'''
Patch Landlord Remittance after adding an autonaming column we need to rename existing docs
'''

from __future__ import unicode_literals

import frappe


def execute():
    lr_list = frappe.get_list('Landlord Remittance', fields=["name"], filters=[], order_by="creation")
    # Rename documents
    start_val = 1
    prefix = 'LAR-'
    for n in lr_list:
        new_name = prefix + str(start_val).zfill(5)
        new_doc = frappe.rename_doc("Landlord Remittance", n.name, new_name, debug=0, force=True)
        start_val = start_val + 1

    frappe.db.commit()
