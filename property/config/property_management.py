from __future__ import unicode_literals

from frappe import _


def get_data():
    return [
        {
            "label": _("Documents"),
            "icon": "icon-star",
            "items": [
                {
                    "type": "doctype",
                    "name": "Property",
                    "description": _("Properties database.")
                },
                {
                    "type": "doctype",
                    "name": "Property Unit",
                    "description": _("Property Units database.")
                },
                {
                    "type": "doctype",
                    "name": "Customer",
                    "description": _("Customer database.")
                },
                {
                    "type": "doctype",
                    "name": "Supplier",
                    "description": _("Supplier database.")
                },
                {
                    "type": "doctype",
                    "name": "Owner Contract",
                    "description": _("Contracts with property owners")
                },
                {
                    "type": "doctype",
                    "name": "Tenancy Contract",
                    "description": _("Contracts with tenants")
                },
                {
                    "type": "doctype",
                    "name": "Property Item",
                    "description": _("Manage fittings and fixtures in properties")
                },
                {
                    "type": "doctype",
                    "name": "Property Work Order",
                    "description": _("Generate work orders for works to be done in a property")
                },
                {
                    "type": "doctype",
                    "name": "Landlord Remittance",
                    "description": _("Create a Landlord Remittance based on collected invoices and expenses")
                },
                {
                    "type": "doctype",
                    "name": "Remittance Payment Voucher",
                    "description": _("Make remittance payment to Landlords")
                },
                {
                    "type": "doctype",
                    "name": "Utility Item Measurement",
                    "description": _(
                        "Record and Track measurements (Meter Readings / Units / Monetary Amounts). Enter those here.")
                },
            ]
        },
        {
            "label": _("Setup"),
            "icon": "icon-cog",
            "items": [
                {
                    "type": "doctype",
                    "name": "Property Type",
                    "description": _("Create property types.")
                },
                {
                    "type": "doctype",
                    "name": "Property Item Type",
                    "description": _("Create property item types.")
                },
                {
                    "type": "doctype",
                    "name": "Property Item Master",
                    "description": _("Create and manage property item masters.")
                },
                {
                    "type": "doctype",
                    "name": "Item",
                    "description": _("Create and manage rental invoice items.")
                },
                {
                    "type": "doctype",
                    "name": "Utility Item",
                    "description": _(
                        "Create and manage Utility Items to be used for utility services billing e.g. water"
                        ", electricity etc.")
                },
                {
                    "type": "doctype",
                    "name": "Landlord Email Digest",
                    "description": _("This is used to send email digest to the landlord")
                },
                {
                    "type": "doctype",
                    "name": "Hand Over",
                    "description": _("This is used to facilitate the handover process")
                }
            ]
        },
        {
            "label": _("Main Reports"),
            "icon": "icon-table",
            "items": [

            ]
        },
        {
            "label": _("Standard Reports"),
            "icon": "icon-list",
            "items": [

            ]
        },
        {
            "label": _("Settings"),
            "icon": "icon-table",
            "items": [
                {
                    "type": "doctype",
                    "name": "Property Management Settings",
                    "description": _("Property management module configuration settings.")
                },
                {
                    "type": "doctype",
                    "name": "Billing Period",
                    "description": _("Setup Billing Periods.")
                }
            ]
        },
        {
            "label": _("Help"),
            "icon": "icon-facetime-video",
            "items": [
            ]
        }
    ]
