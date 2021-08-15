// Copyright (c) 2021, Baida and contributors
// For license information, please see license.txt


frappe.ui.form.on('Aid Details', 'item_code', function(frm, cdt, cdn) {
	if (!frm.doc.company){
		frm.clear_table("items");
		frappe.throw({message:__("Please select a Company first."), title: __("Mandatory")});
	}

	var u = locals[cdt][cdn];
	if(!u || !u.item_code)
		return;

	frappe.call({
		method: "beneficiaries.beneficiaries.doctype.beneficiary.beneficiary.get_item_detail",
		args: {item_code: u.item_code, asset_category: u.asset_category, 
			company: frm.doc.company, type: u.type,},
		freeze: true,
		callback: function(msg) {
			console.log(msg);
			if(msg && msg.message){
				u.warehouse = msg.message.warehouse;
				u.income_account = msg.message.income_account;
				u.expense_account = msg.message.expense_account;
				console.log( msg.message.expense_account);
				u.cost_center = msg.message.cost_center;
				u.project = msg.message.project;
				u.project_activities = msg.message.project_activities;
				u.valuation_rate = msg.message.valuation_rate;
				u.rate=msg.message.valuation_rate;
				
				frm.refresh_fields();
			}			
		}
	}); 
});
frappe.ui.form.on("Aid Details", {
	uom:function(frm, cdt, cdn){
		var u = locals[cdt][cdn];
		if(u.uom == null){return;}
		frappe.call({
			method: "beneficiaries.beneficiaries.doctype.beneficiary.beneficiary.get_conversion_factor",
			args: {
				item_code: u.item_code,
				uom : u.uom,
			},
			freeze: true,
			callback: function(msg) {
				if(!msg || !msg.message){msg.message = 1;}
				u.conversion_factor = msg.message;
				u.stock_qty = flt(u.qty) * flt(msg.message);
				frm.refresh_fields();			
			}
		}); 
	}}
);
frappe.ui.form.on('Aid Details', 'qty', function(frm, cdt, cdn) {
	var u = locals[cdt][cdn];
	u.stock_qty = flt(u.qty) * flt(u.conversion_factor);
	cur_frm.cscript.update_row_amount(frm, cdt, cdn);

	
});
frappe.ui.form.on('Aid Details', 'rate', function(frm, cdt, cdn) {	
	cur_frm.cscript.update_row_amount(frm, cdt, cdn);

});

cur_frm.cscript.update_row_amount = function(frm, cdt, cdn){
	var u = locals[cdt][cdn];
	frappe.model.set_value(u.doctype, u.name, "amount", (u.qty * u.rate));
	frm.refresh_fields();	
}
	  
frappe.ui.form.on('Beneficiary','validate',function(frm) {
	
	cur_frm.clear_table("display");
		frm.events.aids_details(frm);
					    
})
// frm.set_query("project_activities", "aids_details", function(doc, cdt, cdn) {
// 	var u = locals[cdt][cdn];
// 	return {
// 		filters: {
// 			project: u.project,
// 		}
// 	};
// });
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
		
		frappe.dynamic_link = {doc: frm.doc, fieldname: 'name', doctype: 'Beneficiary'}
			frm.toggle_display(['address_html','contact_html'], !frm.doc.__islocal);
	
			if(!frm.doc.__islocal) {
				frappe.contacts.render_address_and_contact(frm);
			
			}
				else {
				frappe.contacts.clear_address_and_contact(frm);
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
	// 	$.each(frm.doc.display,function(i,row)
	// {
	// 	if (row.state==0)
	// 	{
	// 		row.grid.remove();
	// 	}
	// 	cur_frm.refresh();

	// });
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

//   frappe.ui.form.on("Aid Details", {
// 	uom:function(frm, cdt, cdn){
// 		var u = locals[cdt][cdn];
// 		if(u.uom == null){return;}
// 		frappe.call({
// 			method: "beneficiaries.beneficiaries.doctype.beneficiary.beneficiary.get_conversion_factor",
// 			args: {
// 				item_code: u.item_code,
// 				uom : u.uom,
// 			},
// 			freeze: true,
// 			callback: function(msg) {
// 				if(!msg || !msg.message){msg.message = 1;}
// 				u.conversion_factor = msg.message;
// 				u.stock_qty = flt(u.qty) * flt(msg.message);
// 				frm.refresh_fields();			
// 			}
// 		}); 
// 	  },
// // 	  download_pdf: function(frm, cdt, cdn) {
// // 		var child = locals[cdt][cdn]

// // 		var w = window.open(
// // 			frappe.urllib.get_full_url("/api/method/erpnext.buying.doctype.request_for_quotation.request_for_quotation.get_pdf?"
// // 			+"doctype="+encodeURIComponent(frm.doc.doctype)
// // 			+"&name="+encodeURIComponent(frm.doc.name)
// // 			+"&supplier_idx="+encodeURIComponent(child.idx)
// // 			+"&no_letterhead=0"));
// // 		if(!w) {
// // 			frappe.msgprint(__("Please enable pop-ups")); return;
// // 		}
// // 	},
//    });

// frappe.ui.form.on('Aid Details', 'item_code', function(frm, cdt, cdn) {
// 	if (!frm.doc.company){
// 		frm.clear_table("items");
// 		frappe.throw({message:__("Please select a Company first."), title: __("Mandatory")});
// 	}

// 	var u = locals[cdt][cdn];
// 	if(!u || !u.item_code)
// 		return;

// 	frappe.call({
// 		method: "beneficiaries.beneficiaries.doctype.beneficiary.beneficiary.get_item_detail",
// 		args: {item_code: u.item_code, is_fixed_asset: u.is_fixed_asset, asset_category: u.asset_category, 
// 			company: frm.doc.company, type: u.type,},
// 		freeze: true,
// 		callback: function(msg) {
// 			console.log(msg);
// 			if(msg && msg.message){
// 				u.warehouse = msg.message.warehouse;
// 				u.income_account = msg.message.income_account;
// 				u.expense_account = msg.message.expense_account;
// 				if(frm.doc.type == 'Asset')
// 					u.asset_location = msg.message.asset_location;
// 				u.cost_center = msg.message.cost_center;
// 				u.project = msg.message.project;
// 				u.project_activities = msg.message.project_activities;
// 				u.valuation_rate = msg.message.valuation_rate;
				
// 				frm.refresh_fields();
// 			}			
// 		}
// 	}); 
// });

// frappe.ui.form.on('Aid Details', 'qty', function(frm, cdt, cdn) {
// 	var u = locals[cdt][cdn];
// 	u.stock_qty = flt(u.qty) * flt(u.conversion_factor);
// 	cur_frm.cscript.update_row_amount(frm, cdt, cdn);
// 	cur_frm.cscript.update_total(frm);
// });
// frappe.ui.form.on('Aid Details', 'rate', function(frm, cdt, cdn) {	
// 	cur_frm.cscript.update_row_amount(frm, cdt, cdn);
// 	cur_frm.cscript.update_total(frm);
// });

// cur_frm.cscript.update_row_amount = function(frm, cdt, cdn){
// 	var u = locals[cdt][cdn];
// 	frappe.model.set_value(u.doctype, u.name, "amount", (u.qty * u.rate));
// }

// cur_frm.cscript.update_total = function(frm){
// 	var qty = 0;
// 	var amount = 0;
// 	frm.doc.items.forEach(function(d){
// 		qty += d.qty;
// 		amount += d.amount;
// 	});
		
// 	// frm.set_value('total_qty', qty || 0);
// 	// frm.set_value('total', amount || 0);
// 	frm.refresh_fields();
// }


// frappe.ui.form.on('Beneficiary Aids Entry', {
// // 	setup: function(frm) {
// //     	frm.fields_dict['beneficiaries'].grid.get_field('beneficiary').get_query = function(frm, cdt, cdn) {
// // 			var child = locals[cdt][cdn];
// // 			return{
// // 				filters: {
// // 					"type": frm.type
// // 				}
// // 			}
// // 	    }	   
// // 	}
// // })


// frappe.ui.form.on('Beneficiary Aids Entry', {
// 	refresh(frm) {
// 	cur_frm.set_query("beneficiary", "beneficiaries", function(doc, cdt, cdn) {
// 	    var d = locals[cdt][cdn];
//     	return{
// 	    	filters: [
		    
// 		    	['Beneficiary', 'type', '=', d.type]
// 	    	]
//             	}
//         });
// 	}
// })








