frappe.provide("frappe.treeview_settings");

frappe.treeview_settings['Beneficiary Family Member'] = {
	get_tree_nodes: "beneficiaries.beneficiaries.doctype.beneficiary_family_member.beneficiary_family_member.get_children",
	add_tree_node: "beneficiaries.beneficiaries.doctype.beneficiary_family_member.beneficiary_family_member.add_node",
	filters: [
		{
			fieldname: "beneficiary",
			fieldtype:"Link",
			options: "Beneficiary Request",
			label: __("Beneficiary"),
		},
		{
			fieldname: "beneficiary_family_members",
			fieldtype:"Link",
			options: "Beneficiary Family Member",
			label: __("Beneficiary Name"),
			get_query: function() {
				var me = frappe.treeview_settings['Beneficiary Family Member'];
				var beneficiary = me.page.fields_dict.beneficiary.get_value();
				var args = [["Beneficiary Family Member", 'is_group', '=', 1]];
				if(beneficiary){
					args.push(["Beneficiary Family Member", 'beneficiary', "=", beneficiary]);
				}
				return {
					filters: args
				};
			}
		}
	],
	breadcrumb: "Beneficiaries",
	get_tree_root: false,
	root_label: "All Beneficiaries",
	ignore_fields: ["parent_beneficiary_family_members"],
	onload: function(me) {
		frappe.treeview_settings['Beneficiary Family Member'].page = {};
		$.extend(frappe.treeview_settings['Beneficiary Family Member'].page, me.page);
		me.make_tree();
	},
	toolbar: [
		{
			label:__("Add Multiple"),
			condition: function(node) {
				return node.expandable;
			},
			click: function(node) {
				this.data = [];
				const dialog = new frappe.ui.Dialog({
					title: __("Add Multiple Beneficiary Family Member"),
					fields: [
						{
							fieldname: "multiple_beneficiaries", fieldtype: "Table",
							in_place_edit: true, data: this.data,
							get_data: () => {
								return this.data;
							},
							fields: [{
								fieldtype:'Data',
								fieldname:"beneficiary_name",
								in_list_view: 1,
								reqd: 1,
								label: __("Name")
							}]
						},
					],
					primary_action: function() {
						dialog.hide();
						return frappe.call({
							method: "beneficiaries.beneficiaries.doctype.beneficiary_family_member.beneficiary_family_member.add_multiple_beneficiaries",
							args: {
								data: dialog.get_values()["multiple_beneficiaries"],
								parent: node.data.value
							},
							callback: function() { }
						});
					},
					primary_action_label: __('Create')
				});
				dialog.show();
			}
		}
	],
	extend_toolbar: true
};