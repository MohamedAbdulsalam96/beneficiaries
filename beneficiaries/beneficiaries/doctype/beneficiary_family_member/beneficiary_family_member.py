# -*- coding: utf-8 -*-
# Copyright (c) 2021, Baida and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe import _, throw
from frappe.desk.form.assign_to import clear, close_all_assignments
from frappe.model.mapper import get_mapped_doc
from frappe.utils import add_days, cstr, date_diff, get_link_to_form, getdate, today
from frappe.utils.nestedset import NestedSet

class BeneficiaryFamilyMember(NestedSet):
	nsm_parnet_field = 'parent_beneficiary_family_members'

	def on_trash(self):
		NestedSet.on_trash(self, allow_root_deletion=True)


@frappe.whitelist()
def add_multiple_beneficiaries(data, parent):
		data = json.loads(data)
		new_doc = {'doctype': 'Beneficiary Family Member', 'parent_beneficiary_family_members': parent if parent!="All Beneficiaries" else ""}
		new_doc['beneficiary'] = frappe.db.get_value('Beneficiary Family Member', {"name": parent}, 'beneficiary') or ""

		for d in data:
			if not d.get("beneficiary_name"): continue
			new_doc['beneficiary_name'] = d.get("beneficiary_name")
			new_task = frappe.get_doc(new_doc)
			new_task.insert()

@frappe.whitelist()
def get_children(doctype, parent, beneficiary_family_member=None, beneficiary=None, is_root=False):

		filters = [['docstatus', '<', '2']]

		if beneficiary_family_member:
			filters.append(['parent_beneficiary_family_members', '=', beneficiary_family_member])
		elif parent and not is_root:
			# via expand child
			filters.append(['parent_beneficiary_family_members', '=', parent])
		else:
			filters.append(['ifnull(`parent_beneficiary_family_members`, "")', '=', ''])

		if beneficiary:
			filters.append(['beneficiary', '=', beneficiary])

		beneficiaries = frappe.get_list(doctype, fields=[
			'name as value',
			'beneficiary_name as title',
			'is_group as expandable'
		], filters=filters, order_by='name')

		# return tasks
		return beneficiaries

@frappe.whitelist()
def add_node():
		from frappe.desk.treeview import make_tree_args
		args = frappe.form_dict
		args.update({
			"name_field": "beneficiary_name"
		})
		args = make_tree_args(**args)
	
		if args.parent_beneficiary_family_member == 'All Beneficiaries' or args.parent_beneficiary_family_member == args.beneficiary:
			args.parent_beneficiary_family_member = None

		frappe.get_doc(args).insert()