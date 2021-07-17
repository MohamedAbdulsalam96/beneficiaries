// Copyright (c) 2021, Baida and contributors
// For license information, please see license.txt
frappe.ui.form.on('Beneficiary','validate',function(frm) {
	cur_frm.clear_table("display");
		frm.events.aids_details(frm);
					    
})
frappe.ui.form.on("Beneficiary", {

	aids_details: function (frm) {
		return frappe.call({
			doc: frm.doc,
			method: 'aids_details',
			callback: function(r) {
				cur_frm.refresh_fields("display");
			}
		})
		
	},
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
		
		if(frm.is_new()) {
			frm.page.clear_primary_action();}
			else{
		frm.add_custom_button(__("Add As User"), function() {
			create_beneficiary_contact(frm);
		}).addClass("btn-primary");}
	
		frappe.dynamic_link = {doc: frm.doc, fieldname: 'name', doctype: 'Beneficiary'}
		frm.toggle_display(['address_html','contact_html'], !frm.doc.__islocal);

		if(!frm.doc.__islocal) {
			frappe.contacts.render_address_and_contact(frm);
		
		}
			else {
			frappe.contacts.clear_address_and_contact(frm);
		}

	 const create_beneficiary_contact = function (frm) {
		 frappe.confirm(__('This will add beneficiary to Beneficaries list . Do you want to proceed?'),
			function() {
				frappe.call({
					method: 'create_beneficiary_contact',
					args: {},
					callback: function() {frm.events.refresh(frm);
						cur_frm.save();
						frm.refresh();
					frm.save();
					if (frm.doc.is_user==1 && frm.doc.has_contact==1 && frm.doc.has_user_permission==1)
					    cur_frm.clear_custom_buttons();
						cur_frm.save();
						frm.refresh();
				},
					doc: frm.doc,
					
				});
				
			},
			);
		}

		
	
	},

	


});
	
// Copyright (c) 2021, Baida and contributors
// For license information, please see license.txt
frappe.ui.form.on('Aid Details', {
	from_date:function(frm){
		set_total_months(frm);
	}
  })
  frappe.ui.form.on('Aid Details', {
	to_date:function(frm){
		set_total_months(frm);
		
	}
  })
  frappe.ui.form.on('Beneficiary', {
	return:function(frm){
	if (frm.doc.return==1)
	{
		frm.events.add_return(frm);
	}
	}
  })
  frappe.ui.form.on('Beneficiary', {
	aid_approval:function(frm){
		cur_frm.clear_table("display");
		frm.events.aids_details(frm);
	}
  })
//   var set_aids=function(frm,cdt,cdn)
//   { console.log('added');
//   cur_frm.clear_table("display");
//    cur_frm.refresh_fields();
//   $.each(frm.doc.aid_details,function(i,row)
//   {
// 	  for( i=0;i<row.number_of_months;i++)
// 	  {
// 		var childTable = cur_frm.add_child("display");
// 	    childTable.aid_type=row.aid_type;
// 		childTable.type=row.type;
// 		childTable.amount=row.amount;
// 		childTable.item=row.item;
// 		var start_date= new Date(row.from_date);
		
// 		childTable.exchange_date=(start_date.setMonth(start_date.getMonth() + i+1));
// 		console.log(row.from_date);
// 		console.log(new Date(row.from_date));
// 		console.log(new Date(childTable.exchange_date));
// 	  }
	
	
// 	cur_frm.refresh_fields("display");
	
//   })
//   }
 
  var set_total_months=function(frm,cdt,cdn)
  {
	//var d = locals[cdt][cdn]; 
	 console.log('total');
	 $.each(frm.doc.aid_details,function(i,row)
	 {            
		var start_date= new Date(row.from_date);
		var end_date=new Date(row.to_date);
		var numberOfMonths = (end_date.getFullYear() - start_date.getFullYear()) * 12 + (end_date.getMonth() - start_date.getMonth()) + 1;	
		row.number_of_months=numberOfMonths;
		//cur_frm.refresh_fields("aid_details");
		console.log(numberOfMonths);
		
	 })

  }






