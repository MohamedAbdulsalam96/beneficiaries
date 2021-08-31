frappe.ready(function() {
	// bind events here
	frappe.web_form.after_load = () => {
		frappe.msgprint('المساعدات خاصة بسكان العنيزة فقط ');}
		
	
	
	
	frappe.web_form.validate = () => {
		let data = frappe.web_form.get_values();
		// if (data.promise_correct_data ==0) {
		// 	frappe.msgprint(' يجب التأشير على أتعهد بصحة البيانات ');
		// 	return ;}
		frappe.web_form.doc['fees'] = data.fees;
		
		// frappe.web_form.doc['obligation'] = data.obligation;
		// frappe.web_form.doc['family_own'] = data.family_own;
		  
		return true;
	 };
})