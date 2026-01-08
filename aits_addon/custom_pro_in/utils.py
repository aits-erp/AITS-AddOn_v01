import frappe
from frappe.model.mapper import get_mapped_doc
from erpnext.accounts.report.financial_statements import get_data, get_period_list

from frappe.utils import fmt_money


@frappe.whitelist()
def make_proforma_invoice(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.ignore_permissions = True
        target.run_method("set_missing_values")

    # Function to map Sales Order Item → Proforma Invoice Item
    def set_item_details(source_doc, target_doc, source_parent=None):
        target_doc.item_name = source_doc.item_name
        target_doc.description = source_doc.description
        target_doc.uom = source_doc.uom
        target_doc.qty = source_doc.qty
        target_doc.rate = source_doc.rate
        target_doc.amount = source_doc.amount
        target_doc.delivery_date = source_doc.delivery_date

    doclist = get_mapped_doc(
        "Sales Order",
        source_name,
        {
            "Sales Order": {
                "doctype": "Proforma Invoice",
                "field_map": {
                    "name": "sales_order",
                    "customer": "customer",
                    "transaction_date": "posting_date",
                    "company": "company"
                },
            },
            "Sales Order Item": {
                "doctype": "Proforma Invoice Item",
                "field_map": {
                    "parent": "sales_order",
                    "uom": "uom",
                     "delivery_date": "delivery_date"
                },
                "postprocess": set_item_details,  # ✅ Correct function reference
            },
        },
        target_doc,
        set_missing_values,
    )

    return doclist








def build_tree(rows, currency=None):
    """Convert financial statement rows into a nested tree structure for frappe.ui.Tree"""
    tree = []
    lookup = {}

    # First pass: create all nodes
    for row in rows:
        if not row.get("account_name"):
            continue

        node = {
            "label": f"{row['account_name']} ({fmt_money(row.get('total') or 0, currency)})",
            "value": row.get("account"),
            "expandable": 1 if row.get("is_group") else 0,
            "children": []
        }

        lookup[row["account"]] = node

    # Second pass: attach to parents
    for row in rows:
        account = row.get("account")
        parent = row.get("parent_account")

        if not account or account not in lookup:
            continue

        node = lookup[account]

        if parent and parent in lookup:
            lookup[parent]["children"].append(node)
        else:
            tree.append(node)  # root node

    return tree

@frappe.whitelist()
def get_balance_sheet_data():
    company = frappe.defaults.get_user_default("Company")
    fiscal_year = frappe.defaults.get_user_default("fiscal_year")

    period_list = get_period_list(fiscal_year, fiscal_year, None, None,
                                  "Fiscal Year", "Yearly", company=company)

    currency = frappe.get_cached_value("Company", company, "default_currency")

    assets = get_data(company, "Asset", "Debit", period_list) or []
    liabilities = get_data(company, "Liability", "Credit", period_list) or []
    equity = get_data(company, "Equity", "Credit", period_list) or []
    income = get_data(company, "Income", "Credit", period_list) or []
    expenses = get_data(company, "Expense", "Debit", period_list) or []

    return {
        "assets_income": build_tree(assets + income, currency),
        "liabilities_expenses": build_tree(liabilities + equity + expenses, currency),
    }
