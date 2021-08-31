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

class BeneficiaryAid(Document):
	def onload(self):
		self.validate_check_state_aid_details()

	def on_submit(self):
		self.validate_decision_date()
	
	# def validate(self):
	# 	self.aids_details()
	def validate_decision_date(self):
		ben = frappe.get_doc("Beneficiary", self.beneficiary)
		ben.date_of_decision=date.today()
		ben.renewal_date=add_months(ben.date_of_decision,12)
		ben.save()

	def validate_check_state_aid_details(self):
	
		for aid in self.get("aid_details"):
			f=True
			for row in self.get("items"):
				if row.aid_no==aid.aid_no and row.state==0:
					f=False
			if f==True:
				aid.state=1

	
		
	def aids_details(self):
		i=1
		for row in self.get("aid_details"):
			if not row.from_date:
				row.from_date=date.today()
			if not row.to_date:
				row.to_date= add_months(row.from_date,1)
				row.number_of_months=1
			row.aid_no=i;
			i=i+1
		for aid in self.get("aid_details"):
			if aid.frequency=="Once":
				i=aid.number_of_months
			elif aid.frequency=="Monthly":
				i=1
			elif aid.frequency=="Every 3 Months":
				i=3
			elif aid.frequency=="Every 6 Months":
				i=6
			else:
				i=1
			for f in range(0,aid.number_of_months,i):
				exchange_date =  add_months(aid.from_date,f)
				row = self.append('items', {})
				row.type=aid.type
				row.amount=aid.amount
				row.aid_decision_date=exchange_date
				row.aid_no=aid.aid_no
				row.state=aid.state
