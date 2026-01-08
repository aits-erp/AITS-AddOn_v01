// frappe.ui.form.on('Pricing Rule', {
//     refresh: function(frm) {
//         frm.trigger("toggle_additional_discount");
//         frm.trigger("toggle_promotional_scheme");
//     },

//     additional_discount: function(frm) {
//         frm.trigger("toggle_additional_discount");
//         console.log("additional_discount changed");
//     },

//     promotional_scheme: function(frm) {
//         frm.trigger("toggle_promotional_scheme");
//     },

//     toggle_additional_discount: function(frm) {
//         if (frm.doc.additional_discount) {
//             frm.set_df_property("addl_valid_from", "hidden", 0);
//             frm.set_df_property("addl_valid_to", "hidden", 0);
//             frm.set_df_property("addl_discount_percentage", "hidden", 0);
//         } else {
//             frm.set_df_property("addl_valid_from", "hidden", 1);
//             frm.set_df_property("addl_valid_to", "hidden", 1);
//             frm.set_df_property("addl_discount_percentage", "hidden", 1);
//         }
//     },

//     toggle_promotional_scheme: function(frm) {
//         if (frm.doc.promotional_scheme) {
//             frm.set_df_property("scheme_min_qty", "hidden", 0);
//             frm.set_df_property("scheme_valid_from", "hidden", 0);
//             frm.set_df_property("scheme_valid_to", "hidden", 0);
//         } else {
//             frm.set_df_property("scheme_name", "hidden", 1);
//             frm.set_df_property("scheme_min_qty", "hidden", 1);
//             frm.set_df_property("scheme_valid_from", "hidden", 1);
//             frm.set_df_property("scheme_valid_to", "hidden", 1);
//         }
//     }
// });

frappe.ui.form.on('Pricing Rule', {
    refresh: function(frm) {
        // Toggle visibility on load
        toggle_additional_discount_fields(frm);
        toggle_promotional_scheme_fields(frm);
    },

    additional_discount: function(frm) {
        toggle_additional_discount_fields(frm);
    },

    custom_promotional_scheme: function(frm) {
        toggle_promotional_scheme_fields(frm);
    }
});

function toggle_additional_discount_fields(frm) {
    if (frm.doc.additional_discount) {
        frm.set_df_property('additional_discount_section', 'hidden', 0);
        frm.set_df_property('additional_discounts_table', 'hidden', 0);
    } else {
        frm.set_df_property('additional_discount_section', 'hidden', 1);
        frm.set_df_property('additional_discounts_table', 'hidden', 1);
    }
}

function toggle_promotional_scheme_fields(frm) {
    if (frm.doc.custom_promotional_scheme) {
        frm.set_df_property('custom_promotional_scheme_section', 'hidden', 0);
        frm.set_df_property('scheme_name', 'hidden', 0);
        frm.set_df_property('scheme_valid_from', 'hidden', 0);
        frm.set_df_property('scheme_valid_to', 'hidden', 0);
        frm.set_df_property('scheme_min_qty', 'hidden', 0);
    } else {
        frm.set_df_property('custom_promotional_scheme_section', 'hidden', 1);
        frm.set_df_property('scheme_name', 'hidden', 1);
        frm.set_df_property('scheme_valid_from', 'hidden', 1);
        frm.set_df_property('scheme_valid_to', 'hidden', 1);
        frm.set_df_property('scheme_min_qty', 'hidden', 1);
    }
}


// frappe.ui.form.on('Pricing Rule', {
//     refresh: function(frm) {
//         frm.trigger("toggle_additional_discount");
//     },

//     additional_discount: function(frm) {
//         frm.trigger("toggle_additional_discount");
//     },

//     toggle_additional_discount: function(frm) {
//         // Remove old button / wrapper if any (prevents duplicates)
//         if (frm.addl_toggle_btn) {
//             frm.addl_toggle_btn.remove();
//             frm.addl_toggle_btn = null;
//         }

//         // Always ensure flags are defined
//         if (typeof frm.showing_extra_discount_row === 'undefined') {
//             frm.showing_extra_discount_row = false;
//         }

//         if (frm.doc.additional_discount) {
//             // Show first row always
//             frm.set_df_property("addl_valid_from", "hidden", 0);
//             frm.set_df_property("addl_valid_to", "hidden", 0);
//             frm.set_df_property("addl_discount_percentage", "hidden", 0);

//             // Hide second row initially
//             frm.set_df_property("addl_valid_from_2", "hidden", 1);
//             frm.set_df_property("addl_valid_to_2", "hidden", 1);
//             frm.set_df_property("addl_discount_percentage_2", "hidden", 1);
//             frm.showing_extra_discount_row = false;

//             // Find the wrapper for the field and pin a button to the right
//             const $wrapper = frm.fields_dict["additional_discount"].$wrapper;

//             // ensure relative positioning so absolute button can be positioned
//             $wrapper.css("position", "relative");

//             // create button and position it visually to the right center
//             const $btn = $(`<span title="Add extra discount row" 
//                                style="cursor:pointer;font-weight:bold;font-size:18px; user-select:none;">
//                                ➕
//                            </span>`)
//                 .css({
//                     position: "absolute",
//                     right: "200px",
//                     top: "50%",
//                     transform: "translateY(-50%)",
//                     color: "purple",
//                     padding: "2px 6px",
//                     "border-radius": "4px",
//                 });

//             // attach but do not append inside the label (so clicks don't toggle checkbox)
//             $wrapper.append($btn);
//             frm.addl_toggle_btn = $btn;

//             // click handler
//             $btn.on("click", function(e) {
//                 e.stopPropagation(); // prevent checkbox toggle or label click
//                 // toggle second row independent of checkbox
//                 if (!frm.showing_extra_discount_row) {
//                     frm.set_df_property("addl_valid_from_2", "hidden", 0);
//                     frm.set_df_property("addl_valid_to_2", "hidden", 0);
//                     frm.set_df_property("addl_discount_percentage_2", "hidden", 0);
//                     frm.showing_extra_discount_row = true;
//                     $btn.text("➖").css("color", "red");
//                 } else {
//                     frm.set_df_property("addl_valid_from_2", "hidden", 1);
//                     frm.set_df_property("addl_valid_to_2", "hidden", 1);
//                     frm.set_df_property("addl_discount_percentage_2", "hidden", 1);
//                     // clear values on hide
//                     frm.set_value("addl_valid_from_2", null);
//                     frm.set_value("addl_valid_to_2", null);
//                     frm.set_value("addl_discount_percentage_2", null);
//                     frm.showing_extra_discount_row = false;
//                     $btn.text("➕").css("color", "purple");
//                 }

//                 // Refresh fields to ensure UI updates immediately
//                 frm.refresh_field("addl_valid_from");
//                 frm.refresh_field("addl_valid_to");
//                 frm.refresh_field("addl_discount_percentage");
//                 frm.refresh_field("addl_valid_from_2");
//                 frm.refresh_field("addl_valid_to_2");
//                 frm.refresh_field("addl_discount_percentage_2");
//             });

//         } else {
//             // Checkbox unchecked: hide everything and remove button
//             frm.set_df_property("addl_valid_from", "hidden", 1);
//             frm.set_df_property("addl_valid_to", "hidden", 1);
//             frm.set_df_property("addl_discount_percentage", "hidden", 1);

//             frm.set_df_property("addl_valid_from_2", "hidden", 1);
//             frm.set_df_property("addl_valid_to_2", "hidden", 1);
//             frm.set_df_property("addl_discount_percentage_2", "hidden", 1);
//             frm.showing_extra_discount_row = false;

//             if (frm.addl_toggle_btn) {
//                 frm.addl_toggle_btn.remove();
//                 frm.addl_toggle_btn = null;
//             }

//             // refresh fields
//             frm.refresh_field("addl_valid_from");
//             frm.refresh_field("addl_valid_to");
//             frm.refresh_field("addl_discount_percentage");
//             frm.refresh_field("addl_valid_from_2");
//             frm.refresh_field("addl_valid_to_2");
//             frm.refresh_field("addl_discount_percentage_2");
//         }
//     }
// });
