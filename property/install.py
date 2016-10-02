# -*- coding: utf-8 -*-
# Copyright (c) 2015, Bituls Company Limited and contributors
# For license information, please see license.txt

import frappe
from property.property_management.utils import disable_quick_entry
from frappe.utils.fixtures import sync_fixtures


def before_tests():
    sync_fixtures('property')


def after_install():
    disable_quick_entry('Item')
    frappe.db.commit()