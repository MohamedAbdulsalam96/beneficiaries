# -*- coding: utf-8 -*-
# Copyright (c) 2021, Baida and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff

class BeneficiaryDecision(Document):
	def get_existing_beneficiary_list(self):
		"""
			Returns list of active beneficiary based on selected criteria
			and for which type exists
		"""
		return frappe.db.sql_list("""select beneficiary_family_member as beneficiary_family_member from `tabFamily Members Info` 
		where parentfield='members' and parent=%s order by beneficiary_family_member ASC""",self.beneficiary_family_member)

	def get_beneficiary_list(self):
		"""
			Returns list of active beneficiaries based on selected criteria
			and for which type exists
		"""
		return frappe.db.sql("""select ac.name as beneficiary_family_member, ac.beneficiary_name as beneficiary_name from `tabBeneficiary Family Member` ac 
		where ac.parent_beneficiary_family_members=%s and ac.beneficiary=%s """,[self.beneficiary_family_member, self.beneficiary_request], as_dict=True)

	def fill_beneficiary(self):			
		#self.set('work_plan_details', [])
		members = self.get_beneficiary_list()
		if not members:
			frappe.throw(_("No members for the mentioned type"))
		existing_members=self.get_existing_beneficiary_list()
		for d in members:
			if d.beneficiary_family_member not in existing_members:
				self.append('members', d)
		
		self.number_of_members_in_need = len(members)
		#self.sort_details()

	def fill_aid_logs(self):			
		self.create_logs()

	def create_logs(self):
		if self.aids:
			for m in self.get("aids"):
				child = frappe.new_doc("display")
				child.update({
					'aid_type': 'aid_type',
					'amount': 'amount',
					
				})
				aids.items.append(child)
				# for d in self.get("display"):

				# log_args = frappe._dict({
				# 	"doctype": "Display Aids",
				# 	"aid_entry": self.name,
				# 	"tpye": self.type,
				# 	"beneficiary": m.beneficiary,
				# 	"aid_period": self.aid_period,
				# })
				# il = frappe.get_doc(log_args)
				# il.insert()

