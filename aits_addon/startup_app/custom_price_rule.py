import json
import frappe

from frappe.utils import cint, flt, add_days, getdate, nowdate
from erpnext.stock.get_item_details import (
    get_basic_details,
    get_default_bom,
    get_gross_profit,
    get_item_tax_map,
    get_item_tax_template,
    get_party_item_code,
    get_pos_profile_item_details,
    get_price_list_rate,
    process_args,
    process_string_args,
    remove_standard_fields,
    set_valuation_rate,
    update_bin_details,
    update_party_blanket_order,
    update_stock,
    validate_item_details,
)
from erpnext.accounts.doctype.pricing_rule.pricing_rule import get_pricing_rule_for_item


# ---------------------------------------------------------------------------
# (Optional) Your custom get_item_details – unchanged, kept for compatibility.
# We are NOT overriding ERPNext's get_item_details via hooks, so keeping this
# function is harmless. You may delete it if you don't use it elsewhere.
# ---------------------------------------------------------------------------
@frappe.whitelist()
def custom_get_item_details(args, doc=None, for_validate=False, overwrite_warehouse=True):
    args = process_args(args)
    for_validate = process_string_args(for_validate)
    overwrite_warehouse = process_string_args(overwrite_warehouse)

    item = frappe.get_cached_doc("Item", args.item_code)
    validate_item_details(args, item)

    if isinstance(doc, str):
        doc = json.loads(doc)

    if doc:
        args["transaction_date"] = doc.get("transaction_date") or doc.get("posting_date")
        if doc.get("doctype") == "Purchase Invoice":
            args["bill_date"] = doc.get("bill_date")

    out = get_basic_details(args, item, overwrite_warehouse)

    get_item_tax_template(args, item, out)
    out["item_tax_rate"] = get_item_tax_map(
        args.company,
        args.get("item_tax_template") if out.get("item_tax_template") is None else out.get("item_tax_template"),
        as_json=True,
    )

    get_party_item_code(args, item, out)

    if args.get("doctype") in ["Sales Order", "Quotation"]:
        set_valuation_rate(out, args)

    update_party_blanket_order(args, out)

    current_customer = args.customer
    if args.get("doctype") in ["Purchase Order", "Purchase Receipt", "Purchase Invoice"]:
        args.customer = None

    out.update(get_price_list_rate(args, item))
    args.customer = current_customer

    if args.customer and cint(args.is_pos):
        out.update(get_pos_profile_item_details(args.company, args, update_data=True))

    if item.is_stock_item:
        update_bin_details(args, out, doc)

    # sync args with out (missing keys)
    for key, value in out.items():
        if args.get(key) is None:
            args[key] = value

    data = get_pricing_rule_for_item(args, doc=doc, for_validate=for_validate)
    out.update(data)

    if (
        frappe.db.get_single_value("Stock Settings", "auto_create_serial_and_batch_bundle_for_outward")
        and not args.get("serial_and_batch_bundle")
        and (args.get("use_serial_batch_fields") or args.get("doctype") == "POS Invoice")
    ):
        update_stock(args, out, doc)

    if args.transaction_date and item.lead_time_days:
        out.schedule_date = out.lead_time_date = add_days(args.transaction_date, item.lead_time_days)

    if args.get("is_subcontracted"):
        out.bom = args.get("bom") or get_default_bom(args.item_code)

    get_gross_profit(out)

    if args.doctype == "Material Request":
        out.rate = args.rate or out.price_list_rate
        out.amount = flt(args.qty) * flt(out.rate)

    out = remove_standard_fields(out)
    return out

# ---------------------------------------------------------------------------
# Helper: apply "Additional Discount" (your new section) LAST.
# Fields used from Pricing Rule (Custom Fields already in your fixtures):
# - additional_discount (Check)
# - addl_valid_from (Date)
# - addl_valid_to   (Date)
# - addl_discount_percentage (Float)
# ---------------------------------------------------------------------------
# def apply_additional_discount_if_any(pricing_rule, item_details, args):
#     # 1) basic flag / percentage checks
#     if not flt(getattr(pricing_rule, "additional_discount", 0)):
#         return

#     addl_pct = flt(getattr(pricing_rule, "addl_discount_percentage", 0))
#     if addl_pct == 0:
#         return

#     # 2) date window (inclusive)
#     txn_date = getdate(args.get("transaction_date") or args.get("posting_date") or nowdate())
#     vfrom = getattr(pricing_rule, "addl_valid_from", None)
#     vto = getattr(pricing_rule, "addl_valid_to", None)
#     if vfrom:
#         vfrom = getdate(vfrom)
#         if txn_date < vfrom:
#             return
#     if vto:
#         vto = getdate(vto)
#         if txn_date > vto:
#             return

#     # 3) compute base and current discount
#     #    base = (possibly updated) price_list_rate after earlier rules
#     base = flt(item_details.get("price_list_rate") or args.get("price_list_rate") or 0)
#     if base <= 0:
#         return

#     current_disc_amt = flt(item_details.get("discount_amount") or 0)
#     net_after_existing = base - current_disc_amt
#     if net_after_existing <= 0:
#         return

#     # 4) apply extra discount on the already-discounted price
#     extra_disc_amt = flt(net_after_existing * (addl_pct / 100.0))
#     item_details["discount_amount"] = current_disc_amt + extra_disc_amt

#     # 5) recompute discount % for consistency
#     item_details["discount_percentage"] = flt(item_details["discount_amount"] * 100.0 / base)

#     # 6) optional diagnostics (handy in reports/debug; harmless if not used)
#     item_details["addl_discount_amount"] = extra_disc_amt
#     item_details["addl_discount_applied"] = 1

# def apply_additional_discount_if_any(pricing_rule, item_details, args):
#     """
#     Apply 'Additional Discount' in 1st row and optionally 2nd row (if provided),
#     in sequence, each respecting its date window and applying on already-discounted price.
#     """
#     # --- Helper to apply one row ---
#     def apply_row(vfrom, vto, pct):
#         if not flt(pct):
#             return 0.0

#         txn_date = getdate(args.get("transaction_date") or args.get("posting_date") or nowdate())
#         if vfrom and txn_date < getdate(vfrom):
#             return 0.0
#         if vto and txn_date > getdate(vto):
#             return 0.0

#         base = flt(item_details.get("price_list_rate") or args.get("price_list_rate") or 0)
#         current_disc_amt = flt(item_details.get("discount_amount") or 0)
#         net_after_existing = base - current_disc_amt
#         if net_after_existing <= 0:
#             return 0.0

#         extra = flt(net_after_existing * (pct / 100.0))
#         item_details["discount_amount"] = current_disc_amt + extra
#         item_details["discount_percentage"] = flt(item_details["discount_amount"] * 100.0 / base)
#         return extra

#     # --- Row 1 ---
#     row1_pct = flt(getattr(pricing_rule, "addl_discount_percentage", 0))
#     row1_from = getattr(pricing_rule, "addl_valid_from", None)
#     row1_to = getattr(pricing_rule, "addl_valid_to", None)
#     addl1 = apply_row(row1_from, row1_to, row1_pct)

#     # --- Row 2 (if second row fields exist) ---
#     row2_pct = flt(getattr(pricing_rule, "addl_discount_percentage_2", 0))
#     row2_from = getattr(pricing_rule, "addl_valid_from_2", None)
#     row2_to = getattr(pricing_rule, "addl_valid_to_2", None)
#     addl2 = apply_row(row2_from, row2_to, row2_pct)

#     # --- Diagnostics ---
#     item_details["addl_discount_amount_1"] = addl1
#     item_details["addl_discount_amount_2"] = addl2
#     item_details["addl_discount_applied"] = 1 if (addl1 or addl2) else 0

def apply_additional_discount_if_any(pricing_rule, item_details, args):
    """
    Apply 'Additional Discount' rows from the child table in sequence,
    each respecting its date window, optional quantity filter, and applying
    on already-discounted price.
    """
    txn_date = getdate(args.get("transaction_date") or args.get("posting_date") or nowdate())
    item_qty = flt(item_details.get("qty") or args.get("qty") or 0)
    base_rate = flt(item_details.get("price_list_rate") or args.get("price_list_rate") or 0)

    if not getattr(pricing_rule, "additional_discounts_table", None):
        return

    applied_discounts = []
    total_extra_discount = 0.0
    current_discount_amt = flt(item_details.get("discount_amount") or 0)

    for row in pricing_rule.additional_discounts_table:
        pct = flt(getattr(row, "additional_discount_", 0))
        vfrom = getattr(row, "valid_from", None)
        vto = getattr(row, "valid_to", None)
        qty_req = flt(getattr(row, "quantity_optional", 0))

        # Skip if invalid or 0%
        if not pct:
            continue

        # Date validation
        if vfrom and txn_date < getdate(vfrom):
            continue
        if vto and txn_date > getdate(vto):
            continue

        # Quantity validation (if provided)
        if qty_req and item_qty < qty_req:
            continue

        # Apply this row's discount sequentially
        net_after_existing = base_rate - current_discount_amt
        if net_after_existing <= 0:
            continue

        extra_amt = net_after_existing * (pct / 100.0)
        current_discount_amt += extra_amt
        total_extra_discount += extra_amt
        applied_discounts.append({
            "valid_from": vfrom,
            "valid_to": vto,
            "quantity_optional": qty_req,
            "percentage": pct,
            "applied_amount": extra_amt
        })

    # Update final discount info
    if total_extra_discount:
        item_details["discount_amount"] = current_discount_amt
        item_details["discount_percentage"] = flt(item_details["discount_amount"] * 100.0 / base_rate)
        item_details["addl_discount_applied"] = 1
        item_details["addl_discount_rows"] = applied_discounts
    else:
        item_details["addl_discount_applied"] = 0

# ---------------------------------------------------------------------------
def apply_promotional_scheme_if_any(pricing_rule, item_details, args):
    """
    Apply promotional scheme if enabled and conditions are met.
    Conditions:
      - transaction_date within scheme_valid_from / scheme_valid_to
      - item qty >= scheme_min_qty
    Effect:
      - Tag scheme name on item_details
      - (Optional) Apply scheme discount logic if you later add scheme_discount_percentage
    """

    if not getattr(pricing_rule, "custom_promotional_scheme", 0):
        return

    txn_date = getdate(args.get("transaction_date") or args.get("posting_date") or nowdate())
    vfrom = getattr(pricing_rule, "scheme_valid_from", None)
    vto = getattr(pricing_rule, "scheme_valid_to", None)
    min_qty = flt(getattr(pricing_rule, "scheme_min_qty", 0))
    qty = flt(item_details.get("qty") or 0)

    # Check date window
    if vfrom and txn_date < getdate(vfrom):
        return
    if vto and txn_date > getdate(vto):
        return

    # Check minimum quantity
    if min_qty and qty < min_qty:
        return

    # If all conditions pass → tag scheme
    item_details["promotional_scheme_applied"] = 1
    item_details["promotional_scheme_name"] = getattr(pricing_rule, "scheme_name", "")

    # --- Example extension: if later you add a discount field like "scheme_discount_percentage"
    scheme_pct = flt(getattr(pricing_rule, "scheme_discount_percentage", 0))
    if scheme_pct:
        base = flt(item_details.get("price_list_rate") or args.get("price_list_rate") or 0)
        current_disc_amt = flt(item_details.get("discount_amount") or 0)
        net_after_existing = base - current_disc_amt
        if net_after_existing > 0:
            extra = net_after_existing * (scheme_pct / 100.0)
            item_details["discount_amount"] = current_disc_amt + extra
            item_details["discount_percentage"] = flt(item_details["discount_amount"] * 100.0 / base)


# ---------------------------------------------------------------------------
# Your custom version of ERPNext's apply_price_discount_rule
# (keeps your existing custom chain; calls our helper at the very end)
# ---------------------------------------------------------------------------
def custom_apply_price_discount_rule(pricing_rule, item_details, args):
    item_details.pricing_rule_for = pricing_rule.rate_or_discount

    # --- existing margin handling (unchanged) ---
    if (pricing_rule.margin_type in ["Amount", "Percentage"] and pricing_rule.currency == args.currency) or (
        pricing_rule.margin_type == "Percentage"
    ):
        item_details.margin_type = pricing_rule.margin_type
        item_details.has_margin = True

        if pricing_rule.apply_multiple_pricing_rules and item_details.margin_rate_or_amount is not None:
            item_details.margin_rate_or_amount += pricing_rule.margin_rate_or_amount
        else:
            item_details.margin_rate_or_amount = pricing_rule.margin_rate_or_amount

    # --- existing Rate handling (unchanged) ---
    if pricing_rule.rate_or_discount == "Rate":
        pricing_rule_rate = 0.0
        if pricing_rule.currency == args.currency:
            pricing_rule_rate = pricing_rule.rate

        if pricing_rule_rate:
            is_blank_uom = pricing_rule.get("uom") != args.get("uom")
            item_details.update(
                {
                    "price_list_rate": pricing_rule_rate * (args.get("conversion_factor", 1) if is_blank_uom else 1),
                }
            )
        item_details.update({"discount_percentage": 0.0})

    # --- existing Discount handling (unchanged from your version) ---
    for apply_on in ["Discount Amount", "Discount Percentage"]:
        if pricing_rule.rate_or_discount != apply_on:
            continue

        field = frappe.scrub(apply_on)

        if pricing_rule.apply_discount_on_rate and item_details.get("discount_percentage"):
            item_details[field] += (100 - item_details[field]) * (pricing_rule.get(field, 0) / 100)

        elif args.price_list_rate:
            value = pricing_rule.get(field, 0)
            calculate_discount_percentage = False

            if field == "discount_percentage":
                field = "discount_amount"

                # Step 1: Initial discount from price_list_rate
                value = flt(args.price_list_rate) * (flt(value) / 100.0)

                discount_sum = flt(args.price_list_rate) - value
                dp_price = discount_sum
                temp_value = value

                # Step 2: Apply custom discounts from fields in fixed order
                discount_components = [
                    ("custom_trade_mark", flt(getattr(pricing_rule, "custom_trade_mark", 0))),
                    ("custom_p_scheme", flt(getattr(pricing_rule, "custom_p_scheme", 0))),
                    ("custom_freight", flt(getattr(pricing_rule, "custom_freight", 0))),
                    ("custom_extra_discount", flt(getattr(pricing_rule, "custom_extra_discount", 0))),
                ]

                # Apply in sequence on the remaining amount
                trade_mark_discount = discount_sum * (discount_components[0][1] / 100.0)
                discount_sum -= trade_mark_discount

                custom_a_discount = discount_sum * (discount_components[1][1] / 100.0)
                discount_sum -= custom_a_discount

                custom_b_discount = discount_sum * (discount_components[2][1] / 100.0)
                discount_sum -= custom_b_discount

                custom_c_discount = discount_sum * (discount_components[3][1] / 100.0)
                discount_sum -= custom_c_discount

                net_price = discount_sum
                value = temp_value + trade_mark_discount + custom_a_discount + custom_b_discount + custom_c_discount

                # GST component
                gst_price = flt(args.price_list_rate) - value
                final_gst_price = gst_price - (gst_price / (1 + (flt(pricing_rule.custom_gst_rate) / 100.0)))
                value = value + final_gst_price

                formula = ((dp_price - net_price) * 100.0) / dp_price if dp_price else 0
                item_details["custom_formula"] = round(formula, 2)

                calculate_discount_percentage = True

            if field not in item_details:
                item_details.setdefault(field, 0)

            item_details[field] += value if pricing_rule else args.get(field, 0)

            if calculate_discount_percentage and args.price_list_rate and item_details.discount_amount:
                item_details.discount_percentage = flt(
                    (flt(item_details.discount_amount) / flt(args.price_list_rate)) * 100.0
                )

        else:
            if field not in item_details:
                item_details.setdefault(field, 0)
            item_details[field] += pricing_rule.get(field, 0) if pricing_rule else args.get(field, 0)

    # --- NEW: apply your "Additional Discount" LAST ---
    apply_additional_discount_if_any(pricing_rule, item_details, args)
    
    # --- NEW: apply promotional scheme after additional discount ---
    apply_promotional_scheme_if_any(pricing_rule, item_details, args)


# ---------------------------------------------------------------------------
# Monkey-patch ERPNext core method with our custom implementation
# ---------------------------------------------------------------------------
import erpnext  # noqa: E402

setattr(
    erpnext.accounts.doctype.pricing_rule.pricing_rule,
    "apply_price_discount_rule",
    custom_apply_price_discount_rule,
)

