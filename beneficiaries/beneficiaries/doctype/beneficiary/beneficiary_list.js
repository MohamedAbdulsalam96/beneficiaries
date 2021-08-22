frappe.listview_settings['Beneficiary'] = {
	add_fields: ["marital_status", "status", "nationality", "address",
		"fee_total", "number_of_needed_members_in_family", "deserve_according_to_base", "home_type"],
	
	onload: function(listview) {
		var method = "beneficiaries.beneficiaries.doctype.beneficiary.beneficiary.set_multiple_request";

		listview.page.add_menu_item(__("Set as Beneficiary User"), function() {
			listview.call_for_selected_items(method);
		});

	
	},


};
