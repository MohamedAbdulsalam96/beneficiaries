// Copyright (c) 2021, Baida and contributors
// For license information, please see license.txt
frappe.ui.form.on('Beneficiary Aids Entry', {
	refresh: function(frm) {
	
	frm.set_df_property("get_beneficiaries", "hidden", frm.doc.docstatus ? 1:0);
	// if (frm.doc.docstatus==1)
	// frm.set_df_property("items", "read_only", 1);
	
			frm.events.show_general_ledger(frm);
	
	},

	show_general_ledger: function(frm) {
		if(frm.doc.docstatus==1) {
			frm.add_custom_button(__('Genral Ledger'), function() {
				frappe.route_options = {
					"voucher_no": frm.doc.name,
					"from_date": frm.doc.posting_date,
					"to_date": frm.doc.posting_date,
					"company": frm.doc.company,
					group_by: ""
				};
				frappe.set_route("query-report", "General Ledger");
			}, "fa fa-table");


			frm.add_custom_button(__('Stock Ledger'), function() {
				frappe.route_options = {
					"voucher_no": frm.doc.name,
					"from_date": frm.doc.posting_date,
					"to_date": frm.doc.posting_date,
					"company": frm.doc.company,
					group_by: ""
				};
				frappe.set_route("query-report", "Stock Ledger");
			}, "fa fa-table");
	 }
	},


	get_beneficiaries: function(frm){
		cur_frm.clear_table("items");
	    
		frm.events.fill_beneficiary(frm);
	},


	fill_beneficiary: function (frm) {
		return frappe.call({
			doc: frm.doc,
			method: 'fill_beneficiary',
			callback: function(r) {
				if (r.docs[0].items){
					frm.save();
					frm.refresh();
					if(frm.doc.type=="عيني"){
						$.each(frm.doc.items,function(i,u){
							// if(u.uom == null){return;}
						frappe.call({
							method: "beneficiaries.beneficiaries.doctype.beneficiary_aids_entry.beneficiary_aids_entry.get_conversion_factor",
							
							args: {
								item_code: u.item_code,
								uom : u.uom,
							},
							freeze: true,
							callback: function(msg) {
								if(!msg || !msg.message){msg.message = 1;}
								u.conversion_factor = msg.message;
								u.qty=flt(-u.qty);
								u.stock_qty = flt(u.qty) * flt(msg.message);
								frm.refresh_fields();			
							}
						});
					});
				
					$.each(frm.doc.items,function(i,u){
						// var u = locals[cdt][cdn];
						if(!u || !u.item_code)			return;
												
								frappe.call({
									method: "beneficiaries.beneficiaries.doctype.beneficiary_aids_entry.beneficiary_aids_entry.get_item_detail",
									args: {item_code: row.item_code, is_fixed_asset: u.is_fixed_asset,asset_category:u.asset_category,
										company: frm.doc.company, type: frm.doc.type,},
									freeze: true,
									callback: function(msg) {
										console.log(msg);
										if(msg && msg.message){
											u.warehouse = msg.message.warehouse;
											u.income_account = msg.message.income_account;
											u.expense_account = msg.message.expense_account;
											if(frm.doc.type == 'Asset')
												u.asset_location = msg.message.asset_location;
											u.cost_center = msg.message.cost_center;
											u.project = msg.message.project;
											u.project_activities = msg.message.project_activities;
											u.valuation_rate = msg.message.valuation_rate;
											
											frm.refresh_fields();
										}			
									}
								}); 
							});
						}	
			}
			}
		})
	}
});
frappe.ui.form.on("Beneficiary Aids Entry", 
	'validate',function(frm){
	
		});
	

cur_frm.cscript.update_row_amount = function(frm, cdt, cdn){
	var u = locals[cdt][cdn];
	frappe.model.set_value(u.doctype, u.name, "amount", (u.qty * u.rate));
}

cur_frm.cscript.update_total = function(frm){
	var qty = 0;
	var amount = 0;
	frm.doc.items.forEach(function(d){
		qty += d.qty;
		amount += d.amount;
	});
		
	// frm.set_value('total_qty', qty || 0);
	// frm.set_value('total', amount || 0);
	frm.refresh_fields();
}


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

