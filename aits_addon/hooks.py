app_name = "aits_addon"
app_title = "Aits Addon"
app_publisher = "aits"
app_description = "Add on for all the doctypes and customization of AITS"
app_email = "nikhil@aitsind.com"
app_license = "mit"

# credit debit note hooks
fixtures = [
    {"doctype": "Custom Field", "filters": [
        ["dt", "in", ["Credit Note"]]
    ]},
    {"doctype": "Custom Field", "filters": [
        ["dt", "in", ["Debit Note"]]
    ]},
]

# Startup App Hooks
override_whitelisted_methods = {
    "erpnext.stock.get_item_details.get_item_details": 
        "aits_addon.startup_app.custom_price_rule.custom_get_item_details"
}

fixtures = [
    {   
        "doctype": "Custom Field",
        "filters": [
            ["module", "=", "Startup App"]
        ]
    }
]

# Link JS to Pricing Rule
doctype_js = {
    "Pricing Rule": "public/js/pricing_rule.js"
}

# Proforma Invoice Hooks
doctype_js = {
    "Sales Order": "public/js/sales_order.js",
}

override_whitelisted_methods = {
    "erpnext.selling.doctype.proforma_invoice.proforma_invoice.get_stock_reservation_status":
        "aits_addon.custom_pro_in.doctype.proforma_invoice.proforma_invoice.get_stock_reservation_status",
}

override_doctype_class = {
    "Proforma Invoice": "aits_addon.custom_pro_in.doctype.proforma_invoice.proforma_invoice.ProformaInvoice"
}

# update stock hooks
doc_events = {
    "Sales Invoice": {
        "before_validate": "aits_addon.custom_update_stock.sales.before_validate"
    },
    "Purchase Invoice": {
        "before_validate": "aits_addon.custom_update_stock.purchase.before_validate"
    }
}

#custom_add_ui hooks
app_include_js = "/assets/aits_addon/js/global_dashboard_btn_v2.js"

app_include_css = "/assets/aits_addon/css/customui.css"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "aits_addon",
# 		"logo": "/assets/aits_addon/logo.png",
# 		"title": "Aits Addon",
# 		"route": "/aits_addon",
# 		"has_permission": "aits_addon.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/aits_addon/css/aits_addon.css"
# app_include_js = "/assets/aits_addon/js/aits_addon.js"

# include js, css files in header of web template
# web_include_css = "/assets/aits_addon/css/aits_addon.css"
# web_include_js = "/assets/aits_addon/js/aits_addon.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "aits_addon/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "aits_addon/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "aits_addon.utils.jinja_methods",
# 	"filters": "aits_addon.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "aits_addon.install.before_install"
# after_install = "aits_addon.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "aits_addon.uninstall.before_uninstall"
# after_uninstall = "aits_addon.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "aits_addon.utils.before_app_install"
# after_app_install = "aits_addon.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "aits_addon.utils.before_app_uninstall"
# after_app_uninstall = "aits_addon.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "aits_addon.notifications.get_notification_config"

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

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"aits_addon.tasks.all"
# 	],
# 	"daily": [
# 		"aits_addon.tasks.daily"
# 	],
# 	"hourly": [
# 		"aits_addon.tasks.hourly"
# 	],
# 	"weekly": [
# 		"aits_addon.tasks.weekly"
# 	],
# 	"monthly": [
# 		"aits_addon.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "aits_addon.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "aits_addon.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "aits_addon.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["aits_addon.utils.before_request"]
# after_request = ["aits_addon.utils.after_request"]

# Job Events
# ----------
# before_job = ["aits_addon.utils.before_job"]
# after_job = ["aits_addon.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"aits_addon.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

