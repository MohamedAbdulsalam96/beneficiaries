// Copyright (c) 2021, Baida and contributors
// For license information, please see license.txt

frappe.ui.form.on('Beneficiary Family Member', {
	// refresh: function(frm) {

	// }
});
frappe.ui.form.on('Beneficiary Family Members','validate',function(frm) {
	set_total_fees(frm);
  set_total_obligation(frm);

})
frappe.ui.form.on('Fee Type', {
  fee_in_year:function(frm){
	  set_total_fees(frm);
  }
  
})

frappe.ui.form.on('Beneficiary Obligation', {
  amount:function(frm){
	  set_total_obligation(frm);
  }
})

var set_total_fees=function(frm,cdt,cdn){
  var f=0;
	  $.each(frm.doc.fees,function(i,row)
	  {
		  f=f+row.fee_in_year;
		  frm.refresh();
	  })
  frm.doc.total_of_fees=f;
  
}
var set_total_obligation=function(frm,cdt,cdn){
var ob=0;
	  $.each(frm.doc.obligation,function(i,row)
	  {
		  ob=ob+row.amount;
		  frm.refresh();
	  })
  frm.doc.total_of_obligations=ob;
  
}

frappe.ui.form.on('Beneficiary Family Member', {
	refresh(frm) {
		if (frm.doc.docstatus==1){
			frm.add_custom_button(__("Beneficiary Decision"),
				() => frm.events.make_form(frm), __('Add to Decision List'));
		}	
		
	},
	make_form: function(frm) {
		frappe.route_options = {
		    "beneficiary_family_member": frm.doc.name,
		    
		},
		frappe.set_route("Form", 'Beneficiary Decision', 'New Beneficiary Decision');

	},
	
});
