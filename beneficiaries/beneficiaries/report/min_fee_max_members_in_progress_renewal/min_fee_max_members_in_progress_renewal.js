// Copyright (c) 2016, Baida and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Min Fee Max Members In Progress Renewal"] = {
	"filters": [
		{
			"fieldname":"number_of_needed_members_in_family",
			"label": __("Number Of Member That Live In Home"),
			"fieldtype": "Int",
			// "default": frappe.datetime.get_today(),
			"reqd": 1
		}
		
		

	]
};
