frappe.ready(function() {
	

	frappe.web_form.validate = () => {
		let data = frappe.web_form.get_values();
	
		frappe.web_form.doc['identification'] = data.identification;
		
		frappe.web_form.doc['fees'] = data.fees;
		
		 frappe.web_form.doc['beneficiary_obligation'] = data.beneficiary_obligation;
		 frappe.web_form.doc['family_own'] = data.family_own;
		frappe.web_form.doc['family'] = data.family;
		  
		return true;
	 };
})