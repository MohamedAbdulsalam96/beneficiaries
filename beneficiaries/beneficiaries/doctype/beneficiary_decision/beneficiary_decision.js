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
  frappe.ui.form.on('Beneficiary Decision', {
	aid_approval:function(frm){
		set_aids(frm);
	}
  })
  var set_aids=function(frm,cdt,cdn)
  { console.log('added');
  $.each(frm.doc.aids,function(i,row)
  {
	  for( i=0;i<row.number_of_months;i++)
	  {
		var childTable = cur_frm.add_child("display");
	    childTable.aid_type=row.aid_type;
	  }
	
	
	cur_frm.refresh_fields("display");
  })
  }
 
  var set_total_months=function(frm,cdt,cdn)
  {
	//var d = locals[cdt][cdn]; 
	 console.log('total');
	 $.each(frm.doc.aids,function(i,row)
	 {            
		var start_date= new Date(row.from_date);
		var end_date=new Date(row.to_date);
		var numberOfMonths = (end_date.getFullYear() - start_date.getFullYear()) * 12 + (end_date.getMonth() - start_date.getMonth()) + 1;	
		row.number_of_months=numberOfMonths;
		console.log(numberOfMonths);
		
	 })

  }
frappe.ui.form.on('Beneficiary Decision', {
	get_beneficiary_family_members: function(frm){
		frm.events.fill_beneficiary(frm);
	},
	
	fill_beneficiary: function (frm) {
		return frappe.call({
			doc: frm.doc,
			method: 'fill_beneficiary',
			callback: function(r) {
				if (r.docs[0].members){
					frm.save();
					frm.set_df_property("get_beneficiary_family_members", "hidden", frm.doc.__islocal ? 1:0);
					frm.refresh();
				}
			}
		})
	}
	});

	frappe.ui.form.on('Beneficiary Decision', {
		aid_approval: function(frm){
			frm.events.fill_aid_logs(frm);
		},
		
		fill_aid_logs: function (frm) {
			return frappe.call({
				doc: frm.doc,
				method: 'fill_aid_logs',
				callback: function(r) {
					if (r.docs[0].aids){
						frm.save();
						frm.set_df_property("aid_approval", "hidden", frm.doc.__islocal ? 1:0);
						frm.refresh();
					}
				}
			})
		}
		});



frappe.ui.form.on('Beneficiary Decision', {
setup: function(frm) {
	frm.fields_dict['members'].grid.get_field('beneficiary_family_member').get_query = function(frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		return{
			filters: {
				"type": frm.type
			}
		}
	}	   
}
})


frappe.ui.form.on('Beneficiary Decision', {
refresh(frm) {
cur_frm.set_query("beneficiary_family_member", "members", function(doc, cdt, cdn) {
	var d = locals[cdt][cdn];
	return{
		filters: [
		
			['Beneficiary Family Member', 'type', '=', d.type]
		]
			}
	});
}
})
