// Copyright (c) 2021, Baida and contributors
// For license information, please see license.txt

frappe.ui.form.on('Beneficiary Request', {

	onload:function(frm){
		if (frm.doc.inserted==1)
		frm.page.clear_primary_action();
	},
	refresh: function(frm) {
		{
			
			//frm.clear_custom_buttons();
		
			if(frm.is_new()||frm.doc.inserted==true) {
				frm.page.clear_primary_action();}
			else{
			frm.add_custom_button(__("Add To Beneficiaries"), function() {
				add_to_beneficiaries(frm);
			}).addClass("btn-primary");}
		}
	

	const add_to_beneficiaries = function (frm) {
		frappe.confirm(__('This will add beneficiary to Beneficaries list . Do you want to proceed?'),
			function() {
				frappe.call({
					method: 'add_beneficiary',
					args: {},
					callback: function() {frm.events.refresh(frm);
						cur_frm.save();
						frm.refresh();
					frm.save();},
					doc: frm.doc,
					
				});
				
			},
		
			
		);
	};
},
	
	number_of_needed_members_in_family: function(frm){
		frm.events.is_deserve(frm);
	},

	is_deserve: function (frm) {
		return frappe.call({
			doc: frm.doc,
			method: 'is_deserve',
			callback: function(r) {
				refresh_field("deserve_according_to_base");
			}
		})
	},

	
});

frappe.ui.form.on('Beneficiary Request','validate',function(frm) {
	set_total_fees(frm);
  set_total_obligation(frm);
  frm.events.is_deserve(frm);


})


frappe.ui.form.on('Beneficiary Request', {
	number_of_needed_members_in_family:function(frm){
	
		frm.events.is_deserve(frm);
  }
})

frappe.ui.form.on('Fee Type', {
	fee_in_year:function(frm,cdt,cdn){
		set_total_fees(frm);
		frm.events.is_deserve(frm);
		frm.refresh();
  }
})

frappe.ui.form.on('Fee Type', {
	fee_in_month:function(frm,cdt,cdn){
		set_total_fees(frm);
		frm.events.is_deserve(frm);
		refresh_field("fee_total");
  }
})

// frappe.ui.form.on('Identification Type', {
// 	date_of_issue:function(frm,cdt,cdn){
// 		frm.events.validate_id(frm);
		
//   },
//   date_of_expired:function(frm,cdt,cdn){
// 	frm.events.validate_id(frm);
// }
// })

frappe.ui.form.on('Beneficiary Obligation', {
	amount:function(frm,cdt,cdn){
	set_total_obligation(frm);
	frm.events.is_deserve(frm);
	refresh_field("obligations_total");
  }
})

// var set_deserve=function(frm,cdt,cdn){
//   var base=0;
// var f= frm.doc.fee_in_year;
// var ob=frm.doc.obligations_total;
// var family=frm.doc.number_of_needed_members_in_family;
// base=flt(f-ob)/family;
//  if (base<100 && frm.doc.territory=="العنيزة")
//  {
// 	frm.doc.deserve_according_to_base=true;
//  }
  
// }


var set_total_fees=function(frm,cdt,cdn){
  var f=0;
	  $.each(frm.doc.fees,function(i,row)
	  {   var m=row.fee_in_month;
		  var y=row.fee_in_year;
		  if (m>0)
		  row.fee_in_year=m*12;
		 else if(y>0) 
		  row.fee_in_month=y/12;
		  f=f+row.fee_in_year;
		  frm.refresh();
	  })
  frm.doc.fee_total=f;
  refresh_field("fee_total");
  
}
var set_total_obligation=function(frm,cdt,cdn){
var ob=0;
	  $.each(frm.doc.obligation,function(i,row)
	  {
		  ob=ob+row.amount;
		//   frm.refresh();
	  })
  frm.doc.obligations_total=ob;
  refresh_field("obligations_total");
  
}

// frappe.ui.form.on('Fee Type', {
    
//     fee_type_remove: function(frm, cdt, cdn) {
//         cur_frm.cscript.calculate_final(frm, cdt, cdn)
//     },
//     fee_in_year: function(frm, cdt, cdn) {
//         cur_frm.cscript.calculate_final(frm, cdt, cdn)
//     },
   
// })
// cur_frm.cscript.calculate_final= function(frm, cdt, cdn) {
//         var d = locals[cdt][cdn];
//         // var final =(d.fee_in_year);
//         // frappe.model.set_value(cdt, cdn, 'total', final);
//         var total_f = 0;

//         frm.doc.indicator_detail.forEach(function(d) { total_f += (d.fee_in_year);});
     
//         frm.set_value("fee_total", total_f);
      
//         refresh_field("fee_total");
   
//     }
    
// frappe.ui.form.on('Beneficiary Request', {
// 	validate : function(frm, cdt, cdn) {
//        cur_frm.cscript.calculate_final(frm, cdt, cdn)
   
// 	}
// })


