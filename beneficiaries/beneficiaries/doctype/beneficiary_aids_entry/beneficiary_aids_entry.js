// Copyright (c) 2021, Baida and contributors
// For license information, please see license.txt


frappe.ui.form.on('Aids Entry Details', 'item_code', function(frm, cdt, cdn) {

	var u = locals[cdt][cdn];
	if(!u || !u.item_code)
		return;

	frappe.call({
		method: "beneficiaries.beneficiaries.doctype.beneficiary_aids_entry.beneficiary_aids_entry.get_item_detail",
		args: {item_code: u.item_code, is_fixed_asset: u.is_fixed_asset, asset_category: u.asset_category, 
			company: frm.doc.company, type: frm.doc.type,},
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
					$.each(frm.doc.items,function(i,u){
					frappe.call({
						method: "beneficiaries.beneficiaries.doctype.beneficiary_aids_entry.beneficiary_aids_entry.get_item_detail",
						args: {item_code: u.item_code, is_fixed_asset: u.is_fixed_asset, asset_category: u.asset_category, 
							company: frm.doc.company, type: frm.doc.type,},
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
								frm.save();
								frm.refresh_fields();
							}			
						}
					});
				}); 
			// callback: function(msg) {
				
			// 	if(msg && msg.message){
			// 		frm.doc.items.forEach(function(d){var i=0;
			// 			d.item_code = msg.message[i].item_code;
			// 			console.log(d.item_code);
			// 		i++;
			// 		frm.refresh_field("item_code");
			// 		});
			// 		frm.save();
			// 		frm.refresh();
			// 		frm.refresh_fields();
			// 	}		
			
			 } }
			
		})
	}
});

	
frappe.ui.form.on("Beneficiary Aids Entry", 
	'validate',function(frm){
		console.log("Hiiii");
		$.each(frm.doc.items,function(i,row){
			console.log("Hiiii");
	var item=row.item_code;
	row.item_code=item;
	frm.refresh_field("item_code");
	
		});
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
		
	frm.set_value('total_qty', qty || 0);
	frm.set_value('total', amount || 0);
	frm.refresh_fields();
}

