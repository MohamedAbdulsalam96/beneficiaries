// Copyright (c) 2021, Baida and contributors
// For license information, please see license.txt

frappe.ui.form.on('Beneficiary Aids Payment', {
	setup: function(frm) {
		
		// frm.set_value("party_type", "Beneficiary");
	},
	refresh: function(frm) {
		frm.events.show_general_ledger(frm);
		
	
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
	get_outstanding_invoice: function(frm) {
		const today = frappe.datetime.get_today();
		const fields = [
			{fieldtype:"Section Break", label: __("Posting Date")},
			{fieldtype:"Date", label: __("From Date"),
				fieldname:"from_posting_date", default:frappe.datetime.add_days(today, -30)},
			{fieldtype:"Column Break"},
			{fieldtype:"Date", label: __("To Date"), fieldname:"to_posting_date", default:today},
			{fieldtype:"Section Break", label: __("Due Date")},
			{fieldtype:"Date", label: __("From Date"), fieldname:"from_due_date"},
			{fieldtype:"Column Break"},
			{fieldtype:"Date", label: __("To Date"), fieldname:"to_due_date"},
			{fieldtype:"Section Break", label: __("Outstanding Amount")},
			{fieldtype:"Float", label: __("Greater Than Amount"),
				fieldname:"outstanding_amt_greater_than", default: 0},
			{fieldtype:"Column Break"},
			{fieldtype:"Float", label: __("Less Than Amount"), fieldname:"outstanding_amt_less_than"},
			{fieldtype:"Section Break"},
			{fieldtype:"Check", label: __("Allocate Payment Amount"), fieldname:"allocate_payment_amount", default:1},
		];

		frappe.prompt(fields, function(filters){
			frappe.flags.allocate_payment_amount = true;
			frm.events.validate_filters_data(frm, filters);
			frm.events.get_outstanding_documents(frm, filters);
		}, __("Filters"), __("Get Outstanding Documents"));
	},

	validate_filters_data: function(frm, filters) {
		const fields = {
			'Posting Date': ['from_posting_date', 'to_posting_date'],
			'Due Date': ['from_posting_date', 'to_posting_date'],
			'Advance Amount': ['from_posting_date', 'to_posting_date'],
		};

		for (let key in fields) {
			let from_field = fields[key][0];
			let to_field = fields[key][1];

			if (filters[from_field] && !filters[to_field]) {
				frappe.throw(__("Error: {0} is mandatory field",
					[to_field.replace(/_/g, " ")]
				));
			} else if (filters[from_field] && filters[from_field] > filters[to_field]) {
				frappe.throw(__("{0}: {1} must be less than {2}",
					[key, from_field.replace(/_/g, " "), to_field.replace(/_/g, " ")]
				));
			}
		}
	},

	
	beneficiary:function(frm){
		// frm.set_value("party", frm.doc.beneficiary);
		
			// if (frm.doc.contact_email || frm.doc.contact_person) {
			// 	frm.set_value("contact_email", "");
			// 	frm.set_value("contact_person", "");
			// }
			if(frm.doc.beneficiary_account  && frm.doc.company) {
				if(!frm.doc.posting_date) {
					frappe.msgprint(__("Please select Posting Date before selecting Party"))
					frm.set_value("party", "");
					return ;
				}
				// frm.set_party_account_based_on_party = true;
	
				return frappe.call({
					method: "erpnext.accounts.doctype.payment_entry.payment_entry.get_party_details",
					args: {
						company: frm.doc.company,
						party_type: "Beneficiary",
						party: frm.doc.beneficiary,
						date: frm.doc.posting_date,
						cost_center: frm.doc.cost_center
					},
					callback: function(r, rt) {
						if(r.message) {
							frappe.run_serially([
								() => {
									
										frm.set_value("beneficiary_account", r.message.party_account);
										frm.set_value("account_currency", r.message.party_account_currency);
										frm.set_value("account_balance", r.message.account_balance);
										frm.set_value("party_balance", r.message.party_balance);
								},
								// () => frm.set_value("party_balance", r.message.party_balance),
								// () => frm.set_value("party_name", r.message.party_name),
								// () => frm.clear_table("references"),
								// () => frm.events.hide_unhide_fields(frm),
								// () => frm.events.set_dynamic_labels(frm),
								// () => {
								// 	frm.set_party_account_based_on_party = false;
								// 	if (r.message.bank_account) {
								// 		frm.set_value("bank_account", r.message.bank_account);
								// 	}
								// }
							]);
						}
					}
				});
			}
		
	},


	// party_type: function(frm) {

	// 	let party_types = Object.keys(frappe.boot.party_account_types);
	// 	if(frm.doc.party_type && !party_types.includes(frm.doc.party_type)){
	// 		frm.set_value("party_type", "");
	// 		frappe.throw(__("Party can only be one of "+ party_types.join(", ")));
	// 	}

	// 	if(frm.doc.party) {
	// 		$.each(["party", "party_balance", "paid_from", "paid_to",
	// 			"paid_from_account_currency", "paid_from_account_balance",
	// 			"paid_to_account_currency", "paid_to_account_balance",
	// 			"references", "total_allocated_amount"],
	// 			function(i, field) {
	// 				frm.set_value(field, null);
	// 			})
	// 	}
	// },

	






	// beneficiary: function(frm) {
	// 	if(frm.doc.company) {
	// 		if(!frm.doc.posting_date) {
	// 			frappe.msgprint(__("Please select Posting Date before selecting Party"))
	// 			return ;
	// 		}

	// 		 frappe.call({
	// 			method: "erpnext.accounts.party.get_party_account",
	// 			args: {
	// 				company: frm.doc.company,
	// 				party_type: "Beneficiary",
	// 				party: frm.doc.beneficiary,
	// 			},
	// 			callback: function(r, rt) {
	// 				if(r.message) {
	// 					frm.set_value("party", r.message);
	// 				}
	// 			}
	// 		});
	// 	}
	// },
	// beneficiary_account: function(frm) {
	// 	frm.events.set_account_currency_and_balance(frm, frm.doc.beneficiary_account, "account_currency", "account_balance");
	// },
	// set_account_currency_and_balance: function(frm, account, currency_field, balance_field) {
	// if (frm.doc.posting_date && account) {
	// 	console.log('hhhhhhhhhhhh')
	// 	frappe.call({
	// 		method: "erpnext.accounts.doctype.payment_entry.payment_entry.get_account_details",
	// 		args: {
	// 			"account": account,
	// 			"date": frm.doc.posting_date,
	// 			"cost_center": frm.doc.cost_center
	// 		},
	// 		callback: function(r, rt) {
	// 			if(r.message) {
	// 				console.log(r.message)
	// 				frappe.run_serially([
	// 					() => frm.set_value(currency_field, r.message['account_currency']),
	// 					() => {
	// 						frm.set_value(balance_field, r.message['account_balance']);
	// 					}
	// 				]);
	// 				frm.save();
	// 				frm.refresh_fields();
	// 			}
	// 		}
	// 	});
	// }},
	from_mode_of_payment: function (frm) {
		frm.trigger("check_to_account")
		if (frm.doc.from_mode_of_payment) {
			frappe.call({
				method:'beneficiaries.beneficiaries.doctype.beneficiary_aids_payment.beneficiary_aids_payment.get_payment_account',
				args: {
					"mode_of_payment": frm.doc.from_mode_of_payment,
					"company": frm.doc.company
				},
			
				callback: function (r) {
					if (r.message) {
						frm.set_value("from_account", r.message.account);
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
				frm.set_value("from_account", value.account);
				frm.set_value("from_mode_of_payment", '');
				frappe.db.get_value("Account", { "name": value.account }, "account_currency", function (value2) {
				
				});

			});
		}
		frm.refresh_fields();
		
	},
	bank_account: function (frm) {
		frm.trigger("check_to_account")
		if (frm.doc.bank_account) {
			frappe.db.get_value("Bank Account", { "name": frm.doc.bank_account }, "account", function (value) {
				frm.set_value("bank_account_account", value.account);
				
				frappe.db.get_value("Account", { "name": value.account }, "account_currency", function (value2) {
				
				});

			});
		}
		frm.refresh_fields();},

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
});
