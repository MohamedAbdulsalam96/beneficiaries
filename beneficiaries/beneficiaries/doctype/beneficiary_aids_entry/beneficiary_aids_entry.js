// Copyright (c) 2021, Baida and contributors
// For license information, please see license.txt
frappe.ui.form.on('Beneficiary Aids Entry', {
	refresh: function(frm) {
	
		
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
		cur_frm.clear_table("beneficiaries");
	    
		frm.events.fill_beneficiary(frm);
	},

	fill_beneficiary: function (frm) {
		return frappe.call({
			doc: frm.doc,
			method: 'fill_beneficiary',
			callback: function(r) {
				if (r.docs[0].beneficiaries){
					frm.save();
					frm.refresh();
				}
			}
		})
	}
});

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

