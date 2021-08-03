# -*- coding: utf-8 -*-
# Copyright (c) 2021, Baida and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
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
from frappe.utils.data import add_months
from frappe.utils import cint, cstr, formatdate, flt, getdate, nowdate, get_link_to_form
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from erpnext.stock import get_warehouse_account_map
from erpnext.assets.doctype.asset_category.asset_category import get_asset_category_account
from erpnext.accounts.utils import get_fiscal_year


class BeneficiaryRequest(Document):
	def validate(self):
		self.is_deserve()
		self.validate_values()
		self.created_by = frappe.session.user

	def validate_values(self):
		if (self.number_of_needed_members_in_family > self.number_of_family)  :
			frappe.throw('عدد الافراد المعالين اكبر من عدد افراد الاسرة')
		if (self.number_of_wives > self.number_of_family)  :
			frappe.throw('عدد الزوجات اكبر من عدد افراد الاسرة')
		if (self.the_number_of_household_workers > self.number_of_family)  :
			frappe.throw('عدد الافراد العاملين في المنزل اكبر من عدد افراد الاسرة')
		if ( self.the_number_of_professional_workers > self.number_of_family)  :
			frappe.throw('عدد الافراد العاملين اكبر من عدد افراد الاسرة')
		for m in self.get("id_type"):
			if m.date_of_expired < m.date_of_issue:
				frappe.throw('تاريخ انتهاء الهوية أقل من تاريخ اصدارها')
		


	def get_base(self):
			"""
				Returns list of active beneficiary based on selected criteria
				and for which type exists
			"""
			return frappe.db.sql("""select live_base as live_base,rent_base as rent_base,rent_in_year as rent_in_year,rent_in_five_year as rent_in_five_year
			from `tabThe Base` where number_of_members= %s""",self.number_of_needed_members_in_family, as_dict=True)

	def is_deserve(self):		
		check_is_deserve = self.get_base()
		
		if not check_is_deserve:
			return
		fee_sum=0
		for m in self.get("fees"):
			fee_sum +=m.fee_in_year
		self.fee_total=fee_sum
		obl_sum=0
		for m in self.get("obligation"):
			obl_sum +=m.amount
		self.obligations_total=obl_sum

		result = self.fee_total - self.obligations_total
		if self.territory=="العنيزة" and (self.nationality=="سعودي" or self.nationality=="سوري" )and result <= check_is_deserve[0].live_base:
			self.deserve_according_to_base=True
			self.live_base=check_is_deserve[0].live_base
			if self.home_type== "إيجار":
				self.rent_base=check_is_deserve[0].rent_base
			else:
				self.rent_base=0
			self.rent_in_year=check_is_deserve[0].rent_in_year
			self.rent_in_five_year=check_is_deserve[0].rent_in_five_year
		elif self.territory=="العنيزة" and (self.nationality=="سعودي" or self.nationality=="سوري" ) and result >= check_is_deserve[0].live_base and result <= check_is_deserve[0].rent_base:
			self.deserve_according_to_base=True
			self.live_base=0
			if self.home_type== "إيجار":
				self.rent_base=check_is_deserve[0].rent_base
			else:
				self.rent_base=0
			self.rent_in_year=check_is_deserve[0].rent_in_year
			self.rent_in_five_year=check_is_deserve[0].rent_in_five_year

		
	def add_beneficiary(self):
		
		if self.employee==1:
			beneficiary = frappe.new_doc('Beneficiary')
			beneficiary.beneficiary_name = self.beneficiary_name
			beneficiary.beneficiary_request = self.name
			beneficiary.beneficiary_account=frappe.db.get_single_value('Beneficiary Settings', 'beneficiary_account')
			beneficiary.marital_status = self.marital_status
			beneficiary.nationality = self.nationality
			beneficiary.territory=self.territory
			beneficiary.address=self.address
			beneficiary.gender=self.gender
			beneficiary.phone=self.phone
			beneficiary.mobile=self.mobile
			beneficiary.email=self.email
			pwd=random_string(10)
			beneficiary.default_password=pwd
			for m in self.get("id_type"):
				beneficiary.append('identification', dict(type=m.type, the_number=m.the_number,date_of_issue=m.date_of_issue,date_of_expired=m.date_of_expired))
			for f in self.get("fees"):
				beneficiary.append('fees', dict(fee_type=f.fee_type, fee_in_year=f.fee_in_year,fee_in_month=f.fee_in_month))
			beneficiary.fee_total=self.fee_total
			for ob in self.get("obligation"):
				beneficiary.append('beneficiary_obligation', dict(beneficiary_obligation=ob.beneficiary_obligation,
				obligation_to=ob.obligation_to,amount=ob.amount,number_of_pays=ob.number_of_pays,way_of_pay=ob.way_of_pay,reason_of_obligation=ob.reason_of_obligation,attach=ob.attach))
			beneficiary.obligations_total=self.obligations_total
			beneficiary.home_type=self.home_type
			beneficiary.number_of_rooms=self.number_of_rooms
			beneficiary.home_attach=self.home_type_attachment
			beneficiary.home_state=self.state_of_home
			beneficiary.number_of_family=self.number_of_family
			beneficiary.number_of_wives=self.number_of_wives
			beneficiary.number_of_needed_members_in_family=self.number_of_needed_members_in_family
			beneficiary.the_number_of_professional_workers=self.the_number_of_professional_workers
			beneficiary.the_number_of_household_workers=self.the_number_of_household_workers
			beneficiary.beneficiary_notes=self.beneficiary_notes
			beneficiary.deserve_according_to_base=self.deserve_according_to_base
			beneficiary.live_base=self.live_base
			beneficiary.rent_base=self.rent_base
			beneficiary.rent_in_year=self.rent_in_year
			beneficiary.rent_in_five_year=self.rent_in_five_year
			for f in self.get("family_own"):
				beneficiary.append('family_own', dict(own=f.own, note=f.note))
			if not frappe.db.exists("Beneficiary", beneficiary.name):
				beneficiary.insert()
				frappe.msgprint('Beneficiary Inserted Done :)')
				

				    # create contact from beneficiary
			contact = frappe.new_doc('Contact')
			contact.first_name = self.beneficiary_name
			contact.email_id = self.email
			contact.phone = self.phone
			contact.mobile_no = self.mobile
			contact.is_primary_contact = 1
			contact.append('links', dict(link_doctype='Beneficiary', link_name=beneficiary.name))
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

