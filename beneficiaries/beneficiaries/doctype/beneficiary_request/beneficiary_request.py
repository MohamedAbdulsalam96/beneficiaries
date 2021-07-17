# -*- coding: utf-8 -*-
# Copyright (c) 2021, Baida and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate
from datetime import datetime
import datetime


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
				frappe.throw('تاريخ انتهاء الهوبة أقل من تاريخ اصدارها')
		
		

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


	def add_beneficiary(self):
		
		# benf=frappe.db.sql("""select name from `tabBeneficiary` """, as_dict=True)
		# if self.name is not in benf:
		beneficiary = frappe.new_doc('Beneficiary')
		beneficiary.beneficiary_name = self.beneficiary_name
		beneficiary.beneficiary_request = self.name
		beneficiary.marital_status = self.marital_status
		beneficiary.nationality = self.nationality
		beneficiary.territory=self.territory
		beneficiary.address=self.address
		beneficiary.gender=self.gender
		beneficiary.phone=self.phone
		beneficiary.mobile=self.mobile
		beneficiary.email=self.email
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
			self.inserted=True
		else:
			self.inserted=False

