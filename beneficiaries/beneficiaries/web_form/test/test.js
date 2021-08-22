frappe.ready(function() {
	frappe.web_form.after_load = () => {
		frappe.web_form.on('diff', (field, value) => {
		if (value > 1) {
			frappe.web_form.set_df_property('renewal', 'hidden', 1);
		}
		
	});	
	}



	frappe.web_form.validate = () => {
		// frappe.web_form.on('diff', (field, value) => {
		// 	if (value > 1) {
		// 		frappe.web_form.set_df_property('renewal', 'hidden', 0);
		// 	}
			
		// });
	
		let data = frappe.web_form.get_values();
	
		frappe.web_form.doc['basic_needs'] = data.basic_needs;
		
		frappe.web_form.doc['beneficiary_additional_need'] = data.beneficiary_additional_need;
		
		 frappe.web_form.doc['family'] = data.family;
		
		  
		return true;
	 };
})
