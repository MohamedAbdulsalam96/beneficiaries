# -*- coding: utf-8 -*-
# Copyright (c) 2021, Baida and contributors
# For license information, please see license.txt


from __future__ import unicode_literals
import frappe
import json
from datetime import date
from frappe.model.naming import set_name_by_naming_series
from frappe import _, msgprint, throw
import frappe.defaults
from frappe.utils import flt, cint, cstr, today
from frappe.desk.reportview import build_match_conditions, get_filters_cond
from erpnext.utilities.transaction_base import TransactionBase
from erpnext.accounts.party import validate_party_accounts, get_dashboard_info, get_timeline_data # keep this
from frappe.contacts.address_and_contact import load_address_and_contact, delete_contact_and_address
from frappe.model.rename_doc import update_linked_doctypes
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document
from datetime import datetime
from dateutil.relativedelta import relativedelta
from frappe.permissions import add_user_permission, remove_user_permission, \
	set_user_permission_if_allowed, has_permission
from frappe.utils.password import update_password as _update_password
from frappe.utils import random_string
from frappe.utils.data import add_months,month_diff,add_days
from frappe.utils import cint, cstr, formatdate, flt, getdate, nowdate, get_link_to_form
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from erpnext.stock import get_warehouse_account_map
from erpnext.assets.doctype.asset_category.asset_category import get_asset_category_account
from erpnext.accounts.utils import get_fiscal_year
from frappe.model.mapper import get_mapped_doc
from frappe.utils.user import is_website_user
from erpnext.support.doctype.service_level_agreement.service_level_agreement import get_active_service_level_agreement_for
from frappe.email.inbox import link_communication_to_document
from frappe.utils import flt, has_common

class Beneficiary(Document):
	
	def validate(self):
		self.is_deserve()
		self.validate_renewal_diff()
		if(self.renewal==1):
			self.validate_renewal()
			self.validate_date_of_registration()
			self.validate_renewal_diff()
			
	def validate_renewal_diff(self):
		if self.date_of_decision:
			self.diff=month_diff(self.renewal_date, date.today())
		if self.diff and self.diff < 1 :
			# self.renewal=0
			self.status="Suspended"
	def onload(self):
		"""Load address and contacts in `__onload`"""
		self.validate_renewal_diff()
		load_address_and_contact(self)
	
		
		if ( self.beneficiaries_manager_approve==1 or self.committee_approve==1) and not self.re:
			self.date_of_decision=date.today()
			self.renewal_date=add_months(self.date_of_decision,12)
			self.renewal=0
			re = frappe.new_doc('Beneficiary Renewal')
			re.beneficiary = self.name
			re.date_of_last_decision = self.date_of_decision
			re.date_of_renewal = self.renewal_date
			re.insert()
			self.re="Renewal"
			self.validate_renewal_diff()
		

	def validate_date_of_registration(self):
			self.renewal_date=add_months(self.renewal_date,12)
			self.renewal=0
		

	def validate_renewal(self):
		re = frappe.new_doc('Beneficiary Renewal')
		re.beneficiary = self.name
		re.date_of_last_decision = self.renewal_date
		re.date_of_renewal = add_months(self.renewal_date,12)
		re.insert()
		# self.renewal_date=add_months(self.renewal_date,12)
		self.status="In Progress"

	def get_max_number_of_members(self):
		return frappe.db.sql("""select max(number_of_members) as members from `tabThe Base`""", as_dict=True)

	def get_base(self):
		max_member=self.get_max_number_of_members()[0].members
		if self.number_of_needed_members_in_family > int (max_member):
			members=max_member
		else:
			members=self.number_of_needed_members_in_family
			"""
				Returns list of active beneficiary based on selected criteria
				and for which type exists
			"""
		return frappe.db.sql("""select live_base as live_base,rent_base as rent_base,rent_in_year as rent_in_year,rent_in_five_year as rent_in_five_year
		from `tabThe Base` where number_of_members= %s""",members, as_dict=True)

	def is_deserve(self):		
		check_is_deserve = self.get_base()
		
		if not check_is_deserve:
			return
		fee_sum=0
		for m in self.get("fees"):
			m.fee_in_year=flt(m.fee_in_month * 12)
			fee_sum +=m.fee_in_year
		self.fee_total=fee_sum
		obl_sum=0
		for m in self.get("beneficiary_obligation"):
			obl_sum +=m.amount
		self.obligations_total=obl_sum

		result = self.fee_total - self.obligations_total
		if (self.territory=="Unaizah" or self.territory=="عنيزة") and (self.nationality=="Saudi" or self.nationality=="Syrian" or self.nationality=="سوري" or
		self.nationality=="سعودي")and result <= check_is_deserve[0].live_base:
			self.deserve_according_to_base=True
			self.live_base=check_is_deserve[0].live_base
			if self.home_type== "Rent":
				self.rent_base=check_is_deserve[0].rent_base
			else:
				self.rent_base=0
			self.rent_in_year=check_is_deserve[0].rent_in_year
			self.rent_in_five_year=check_is_deserve[0].rent_in_five_year
		elif (self.territory=="Unaizah" or self.territory=="عنيزة") and (self.nationality=="Saudi" or self.nationality=="Syrian" or self.nationality=="سوري" or
		self.nationality=="سعودي" ) and result >= check_is_deserve[0].live_base and result <= check_is_deserve[0].rent_base:
			self.deserve_according_to_base=True
			self.live_base=0
			if self.home_type== "Rent":
				self.rent_base=check_is_deserve[0].rent_base
			else:
				self.rent_base=0
			self.rent_in_year=check_is_deserve[0].rent_in_year
			self.rent_in_five_year=check_is_deserve[0].rent_in_five_year



@frappe.whitelist()
def set_multiple_request(names):
	names = json.loads(names)
	frappe.msgprint(names)
	for name in names:
		req = frappe.get_doc("Beneficiary", name)
	
		add_beneficiary(req)
		req.save()

def add_beneficiary(self):
			self.owner=self.email
			pwd=random_string(10)
			self.default_password=pwd
			self.save()
				    # create contact from beneficiary
			contact = frappe.new_doc('Contact')
			contact.first_name = self.beneficiary_name
			contact.email_id = self.email
			contact.phone = self.phone
			contact.mobile_no = self.mobile
			contact.is_primary_contact = 1
			contact.append('links', dict(link_doctype='Beneficiary', link_name=self.name))
			if self.email:
				contact.append('email_ids', dict(email_id=self.email, is_primary=1))
			if self.phone:
				contact.append('phone_nos', dict(phone=self.phone, is_primary_mobile_no=1))
			contact.flags.ignore_permissions = self.flags.ignore_permissions
			contact.autoname()
			if not frappe.db.exists("Beneficiary", contact.name):
				contact.insert()
				frappe.msgprint('Beneficiary contact Inserted Done :)')
				# self.has_contact=1

		
			# if self.has_contact==0:
				# frappe.throw("Beneficiary doesn't add to contacts list",raise_exception)
			
			# if self.has_contact==1:
			
			user = frappe.get_doc({
				"doctype": "User",
				"first_name": self.beneficiary_name,
				"email": self.email,
				"Language":"ar",
				"user_type": "Website User",
				"send_welcome_email": 1,
				"role_profile_name":"Beneficiary"
				}).insert(ignore_permissions = True)
			frappe.get_doc("User", self.email).add_roles("Beneficiary")
			
			_update_password(user=self.email, pwd=pwd, logout_all_sessions=0)
			# user.new_password="1234"
			
			# self.is_user=1
			# if self.is_user==0:
			# 	frappe.throw("Beneficiary doesn't add to Users list",raise_exception)

			# if self.is_user==1 and self.has_contact==1:
			
			userpermission = frappe.get_doc({
				"doctype": "User Permission",
				"user": user.email,
				"for_value": self.beneficiary_name,
				"allow": "Beneficiary",
				"is_default":1,
				"apply_to_all_doctypes":0,
				"applicable_for":"Beneficiary"
				
				}).insert()
			# if  frappe.db.exists("Beneficiary", beneficiary.name) and frappe.db.exists("Contact", contact.name) and frappe.db.exists("User", user.email) and  frappe.db.exists("User Permission", userpermission.user):
			self.inserted=True
			# else:
				# self.inserted=False
			# 		self.has_user_permission=1
			# if self.has_user_permission==0:
			# 	frappe.throw("Beneficiary doesn't add to User Permission list",raise_exception)	

