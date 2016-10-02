# -*- coding: utf-8 -*-
from __future__ import unicode_literals

app_name = "property"
app_title = "Property Management"
app_publisher = "Bituls Company Limited"
app_description = "Allows Property Management Agencies to manage properties"
app_icon = "fa fa-building"
app_color = "green"
app_email = "info@bituls.com"
app_version = "0.0.1"
app_license = "GNU"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/property/css/property.css"
# app_include_js = "/assets/property/js/property.js"

# include js, css files in header of web template
# web_include_css = "/assets/property/css/property.css"
# web_include_js = "/assets/property/js/property.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "property.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "property.install.before_install"
# after_install = "property.install.after_install"

after_install = "property.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "property.notifications.get_notification_config"

fixtures = ["Custom Field", "Custom Script", "Workflow State", "Workflow Action", "Workflow", "Role", "Customer Group",
            "Item Group"]

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

doc_events = {
    "Sales Invoice": {
        "before_insert": "property.property_management.hooks.doc_hooks.sales_invoice_arrears",
        "before_submit": "property.property_management.hooks.doc_hooks.sales_invoice_arrears",
        "before_cancel": "property.property_management.hooks.doc_hooks.sales_invoice_cancel"
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"property.tasks.all"
# 	],
# 	"daily": [
# 		"property.tasks.daily"
# 	],
# 	"hourly": [
# 		"property.tasks.hourly"
# 	],
# 	"weekly": [
# 		"property.tasks.weekly"
# 	]
# 	"monthly": [
# 		"property.tasks.monthly"
# 	]
# }

# Testing
# -------

before_tests = "property.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "property.event.get_events"
# }
