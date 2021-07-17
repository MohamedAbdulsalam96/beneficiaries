frappe.ready(function() {
		 
	frappe.web_form.after_load = () => {
		frappe.msgprint('المساعدات خاصة بسكان العنيزة فقط ');}
		
	
	
	
	frappe.web_form.validate = () => {
		let data = frappe.web_form.get_values();
		// if (data.promise_correct_data ==0) {
		// 	frappe.msgprint(' يجب التأشير على أتعهد بصحة البيانات ');
		// 	return ;}
		
		frappe.web_form.doc['id_type'] = data.id_type;
		
		frappe.web_form.doc['fees'] = data.fees;
		
		frappe.web_form.doc['obligation'] = data.obligation;

		  
		return true;
	 };

	 
	 
	 
	 
	//  frappe.require("https://www.google.com/recaptcha/api.js?onload=onloadCallback&render=explicit&type=api.js")
	 
	//  let el = document.querySelector('[data-fieldname="captcha_html_wrapper"]');
	//  window.onloadCallback = function() {
	// 	 captcha = grecaptcha.render(el, {
	// 		 'sitekey' : '6LfeZGobAAAAAOCo_qWdsQkTVdd9ERHJ_B_uTrkk' // Add your site key here.
	// 	 });
	//  }
	 
	//  frappe.web_form.after_load = () => {
	// 	 frappe.web_form.set_df_property('captcha_html_wrapper', 'hidden', 0);
	//  }
	 
	//  frappe.web_form.validate = () => {
	// 	 if (!grecaptcha.getResponse(captcha)) {
	// 		 frappe.throw("Please complete the captcha");
	// 	 } else {
	// 		 frappe.web_form.doc['captcha_html_wrapper'] = '';
	// 		 return true;
	// 	 }
	//  }
	 
	 
	 
	 
	 
	// })
	// bind events here
})