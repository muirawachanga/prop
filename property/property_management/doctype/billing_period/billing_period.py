# -*- coding: utf-8 -*-
# Copyright (c) 2015, Bituls Company Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import date
from frappe.utils import get_first_day, get_last_day, formatdate


class BillingPeriod(Document):
    pass


def create_yearly_periods():
    start = date(date.today().year, 1, 1)
    end = date(date.today().year, 12, 31)
    p_name = start.strftime('Year-%Y')
    doc = frappe.get_doc({"doctype": "Billing Period", "period_name": p_name, "start_date": start, "end_date": end,
                          "period_type": "Yearly"})
    doc.save()


@frappe.whitelist()
def create_monthly_periods():
    for i in range(12):
        start = get_first_day(date(date.today().year, 1, 1), 0, i)
        end = get_last_day(start)
        p_name = start.strftime('%b-%Y')
        doc = frappe.get_doc({"doctype": "Billing Period", "period_name": p_name, "start_date": start, "end_date": end,
                              "period_type": "Monthly"})
        doc.save()
