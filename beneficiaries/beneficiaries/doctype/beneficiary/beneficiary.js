// Copyright (c) 2021, Baida and contributors
// For license information, please see license.txt


	  
frappe.ui.form.on('Beneficiary','validate',function(frm) {
	
		frm.set_df_property("renewal", "hidden", frm.doc.diff<1 ? 0:1);
		frm.set_df_property("renewal", "hidden", frm.doc.diff>1 ? 1:0);
					    
})

frappe.ui.form.on("Beneficiary", {
	
	add_return: function (frm) {
		return frappe.call({
			doc: frm.doc,
			method: 'add_return',
			callback: function(r) {
				cur_frm.refresh_fields("display");
			}
		})
	},
	refresh: function(frm) 
	{
		frm.set_df_property("renewal", "hidden", frm.doc.diff<1 ? 0:1);
		frm.set_df_property("renewal", "hidden", frm.doc.diff>1 ? 1:0);
		frappe.dynamic_link = {doc: frm.doc, fieldname: 'name', doctype: 'Beneficiary'}
			frm.toggle_display(['address_html','contact_html'], !frm.doc.__islocal);
	
			if(!frm.doc.__islocal) {
				frappe.contacts.render_address_and_contact(frm);
			
			}
				else {
				frappe.contacts.clear_address_and_contact(frm);
			}
		
	
	},

	return:function(frm){
	if (frm.doc.return==1)
	{
		frm.events.add_return(frm);
	
	}
	},
	
	validate_date_of_registration: function (frm) {
		return frappe.call({
			doc: frm.doc,
			method: 'validate_date_of_registration',
			callback: function(r) {
				frm.refresh_field("date_of_decision");
					frm.refresh_field("renewal_date");
					frm.set_value();
			}
		})
	
	},
	
	renewal:function(frm){
	
		frm.events.validate_renewal(frm);
		frm.set_df_property("renewal", "hidden", frm.doc.diff<1 ? 1:0);
		frm.set_df_property("renewal", "hidden", frm.doc.diff>1 ? 0:1);
	
	},
	validate_renewal: function (frm) {
		return frappe.call({
			doc: frm.doc,
			method: 'validate_renewal',
			callback: function(r) {
				frm.save();
				frm.refresh_field("date_of_decision");
					frm.refresh_field("renewal_date");
					frm.refresh_field("diff");
			}
		})
	
	},


});
	
