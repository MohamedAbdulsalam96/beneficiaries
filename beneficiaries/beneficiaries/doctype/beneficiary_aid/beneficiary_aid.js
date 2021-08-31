// Copyright (c) 2021, Baida and contributors
// For license information, please see license.txt

frappe.ui.form.on('Beneficiary Aid', {
	aids_details: function (frm) {
		return frappe.call({
			doc: frm.doc,
			method: 'aids_details',
			callback: function(r) {
				
				cur_frm.refresh_fields("items");
				frm.save();
			}
		})
		
	},
	// committee_approve:function(frm){
	// 	frm.events.validate_date_of_registration(frm);
	
	// },
	// beneficiaries_manager_approve:function(frm){
	// 	frm.events.validate_date_of_registration(frm);
	// 	frm.set_value( "re", "Renewal");
	// 	frm.refresh_field("re");
	// 	frm.refresh();
	
	// },
	aid_approval:function(frm){

		cur_frm.clear_table("items");
	   frm.events.aids_details(frm);
   }

	// refresh: function(frm) {

	// }
});
frappe.ui.form.on('Beneficiary Aid','validate',function(frm) {
	
	cur_frm.clear_table("items");
	frm.events.aids_details(frm);
		
})

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




