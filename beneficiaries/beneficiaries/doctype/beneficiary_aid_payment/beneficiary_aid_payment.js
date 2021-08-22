// Copyright (c) 2021, Baida and contributors
// For license information, please see license.txt

frappe.ui.form.on('Beneficiary Aid Payment', {
	validate:function(frm){
		cur_frm.cscript.update_total(frm);
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
					$.each(frm.doc.items,function(i,u){
					frappe.call({
						method: "erpnext.accounts.doctype.payment_entry.payment_entry.get_party_details",
						args: {
							company: frm.doc.company,
							party_type: "Beneficiary",
							party: u.beneficiary,
							date: frm.doc.posting_date,
							cost_center: frm.doc.cost_center
						},
						callback: function(r, rt) {
							if(r.message) {
								
									
											u.paid_from=r.message.party_account;
											u.account_currency= r.message.party_account_currency;
										u.account_balance= r.message.account_balance;
											u.party_balance= r.message.party_balance;
											frm.refresh_fields();
									
							
							}
						}
					});
				});
					frm.save();
					frm.refresh();
						
			 } }
			
		})
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
	}},

	refresh(frm) {
		frm.events.chk_date_enable(frm);
	    frm.events.chk_type(frm);
		frm.events.show_general_ledger(frm);
		

		frm.set_query("paid_from", function() {
			return {
				filters: {
					'account_type': 'Receivable',
					'is_group': 0,
					'company': frm.doc.company
				}
			}
		});
		frm.set_query("warehouse", function() {
			return {
				filters: {
					"is_group": 0,
				}
			}
		});
		frm.set_query("paid_to", function() {
			return {
				filters: {
					"account_type": ["in", ["Bank", "Cash"]],
					"is_group": 0,
					"company": frm.doc.company
				}
			}
		});
		frm.set_query("cost_center", function() {
			return {
				filters: {
					"is_group": 0,
				}
			}
		});


		frm.set_query("project_activities", "items", function(doc, cdt, cdn) {
			var u = locals[cdt][cdn];
			return {
				filters: {
					project: u.project,
				}
			};
		});
	},
	company: function(frm) {
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Company",
				filters: {"name": frm.doc.company},
				fieldname: "cost_center"
			},
			callback: function(r){
				if(r.message){
				console.log(r.message.cost_center);
						frm.set_value( "cost_center", r.message.cost_center);
					
				}
			}
		});
	},
	from_bank_account: function (frm) {
		frm.trigger("check_to_account")
		if (frm.doc.from_bank_account) {
			frappe.db.get_value("Bank Account", { "name": frm.doc.from_bank_account }, "account", function (value) {
				console.log(value.account);
				frm.set_value("paid_to", value.account);
				frm.refresh_fields();
				frm.set_value("mode_of_payment", '');
				frappe.db.get_value("Account", { "name": value.account }, "account_currency", function (value2) {
				
				});

			});
		}
		frm.refresh_fields();
		
	},
	

	
	set_posting_time(frm) {
		frm.events.chk_date_enable(frm);
	},
	chk_date_enable(frm){
		if(frm.doc.set_posting_time == 0){
			frm.set_df_property("posting_date", "read_only", 1);
			frm.set_df_property("posting_time", "read_only", 1);
	    }else{
			frm.set_df_property("posting_date", "read_only", 0);
			frm.set_df_property("posting_time", "read_only", 0);
	    }
	},
	type(frm) {
		$.each(["mode_of_payment", "paid_to", "account_currency", "account_balance"],
				function(i, field) {
					frm.set_value(field, null);
				});
				
		$.each(["total", "total_qty"],
			function(i, field) {
				frm.set_value(field, 0);
		});		
		
		frm.events.chk_type(frm);
		frm.clear_table("items");
	    frm.refresh_fields();
	},

	mode_of_payment: function (frm) {
		frm.trigger("check_to_account")
		if (frm.doc.mode_of_payment) {
			frappe.call({
				method:'beneficiaries.beneficiaries.doctype.beneficiary_aid_payment.beneficiary_aid_payment.get_payment_account',
				args: {
					"mode_of_payment": frm.doc.mode_of_payment,
					"company": frm.doc.company
				},
			
				callback: function (r) {
					if (r.message) {
						frm.set_value("paid_to", r.message.account);
						frm.set_value("from_bank_account", '');
						frappe.db.get_value("Account", { "name": r.message.account }, "account_currency", function (value) {
							
						});
					}
				}
			});
		}
		frm.refresh_fields();
	},
	from_bank_account: function (frm) {
		frm.trigger("check_to_account")
		if (frm.doc.from_bank_account) {
			frappe.db.get_value("Bank Account", { "name": frm.doc.from_bank_account }, "account", function (value) {
				frm.set_value("paid_to", value.account);
				console.log(value.account);
				frm.set_value("mode_of_payment", '');
				frappe.db.get_value("Account", { "name": value.account }, "account_currency", function (value2) {
				
				});

			});
		}
		frm.refresh_fields();
		
	},

	


	paid_to: function(frm) {
		frm.events.set_account_currency_and_balance(frm, frm.doc.paid_to, "account_currency", "account_balance");
	},
	set_account_currency_and_balance: function(frm, account, currency_field, balance_field) {
	if (frm.doc.posting_date && account) {
		frappe.call({
			method: "erpnext.accounts.doctype.payment_entry.payment_entry.get_account_details",
			args: {
				"account": account,
				"date": frm.doc.posting_date,
				"cost_center": frm.doc.cost_center
			},
			callback: function(r, rt) {
				if(r.message) {
					frappe.run_serially([
						() => frm.set_value(currency_field, r.message['account_currency']),
						() => {
							frm.set_value(balance_field, r.message['account_balance']);
						}
					]);
				}
			}
		});
	}
},
warehouse:function(frm){
	frm.doc.items.forEach(function(u){
	   frappe.model.set_value(u.doctype, u.name, "warehouse", frm.doc.warehouse);
	});
   
},
	validate_company: (frm) => {
		if (!frm.doc.company){
			frappe.throw({message:__("Please select a Company first."), title: __("Mandatory")});
		}
	},
	chk_type(frm){
	    if(frm.doc.type == "Cash"){
			frm.set_df_property("paid_to", "reqd", 1);
			frm.set_df_property("mode_of_payment", "reqd", 1);
	    }else{
			frm.set_df_property("paid_to", "reqd", 0);
			frm.set_df_property("mode_of_payment", "reqd", 0);
	    }
	}
})

frappe.ui.form.on("Details", {
	uom:function(frm, cdt, cdn){
		var u = locals[cdt][cdn];
		if(u.uom == null){return;}
		frappe.call({
			method: "beneficiaries.beneficiaries.doctype.beneficiary_aid_payment.beneficiary_aid_payment.get_conversion_factor",
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
	  },
	  download_pdf: function(frm, cdt, cdn) {
		var child = locals[cdt][cdn]

		var w = window.open(
			frappe.urllib.get_full_url("/api/method/erpnext.buying.doctype.request_for_quotation.request_for_quotation.get_pdf?"
			+"doctype="+encodeURIComponent(frm.doc.doctype)
			+"&name="+encodeURIComponent(frm.doc.name)
			+"&supplier_idx="+encodeURIComponent(child.idx)
			+"&no_letterhead=0"));
		if(!w) {
			frappe.msgprint(__("Please enable pop-ups")); return;
		}
	},
  });

  frappe.ui.form.on('Details', 'beneficiary', function(frm, cdt, cdn) {
 
	var u = locals[cdt][cdn];
		if( frm.doc.company) {
			if(!frm.doc.posting_date) {
				frappe.msgprint(__("Please select Posting Date before selecting Party"))
				
				return ;
			}
			

			return frappe.call({
				method: "erpnext.accounts.doctype.payment_entry.payment_entry.get_party_details",
				args: {
					company: frm.doc.company,
					party_type: "Beneficiary",
					party: u.beneficiary,
					date: frm.doc.posting_date,
					cost_center: frm.doc.cost_center
				},
				callback: function(r, rt) {
					if(r.message) {
						
							
									u.paid_from=r.message.party_account;
									u.account_currency= r.message.party_account_currency;
								u.account_balance= r.message.account_balance;
									u.party_balance= r.message.party_balance;
									frm.refresh_fields();
							
					
					}
				}
			});
		}
	
});






frappe.ui.form.on('Details', 'item_code', function(frm, cdt, cdn) {
	if (!frm.doc.company){
		frm.clear_table("items");
		frappe.throw({message:__("Please select a Company first."), title: __("Mandatory")});
	}

	var u = locals[cdt][cdn];
	if(!u || !u.item_code)
		return;

	frappe.call({
		method: "beneficiaries.beneficiaries.doctype.beneficiary_aid_payment.beneficiary_aid_payment.get_item_detail",
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
				if(frm.doc.type == 'Asset')
					u.asset_location = msg.message.asset_location;
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


frappe.ui.form.on('Details', 'qty', function(frm, cdt, cdn) {
	var u = locals[cdt][cdn];
	u.stock_qty = flt(u.qty) * flt(u.conversion_factor);
	cur_frm.cscript.update_row_amount(frm, cdt, cdn);
	cur_frm.cscript.update_total(frm);
});
frappe.ui.form.on('Details', 'rate', function(frm, cdt, cdn) {	
	cur_frm.cscript.update_row_amount(frm, cdt, cdn);
	cur_frm.cscript.update_total(frm);
});

frappe.ui.form.on('Details', 'amount', function(frm, cdt, cdn) {
	cur_frm.cscript.update_total(frm);	
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


