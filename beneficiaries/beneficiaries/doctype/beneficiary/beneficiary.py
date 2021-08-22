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
# sender_field = "raised_by"
class Beneficiary(Document):
	
	def validate(self):
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
		self.validate_check_state_aid_details()
		
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

	def validate_check_state_aid_details(self):
	
		for aid in self.get("aid_details"):
			f=True
			for row in self.get("display"):
				if row.aid_no==aid.aid_no and row.state==0:
					f=False
			if f==True:
				aid.state=1
	

	def add_return(self):
		returnben = frappe.new_doc('Beneficiary Return')
		returnben.beneficiary = self.name
		returnben.employee = self.employee
		returnben.reason = self.reason_of_return
		# returnben.autoname()
		returnben.insert()

	
		
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
				row = self.append('display', {})
				row.type=aid.type
				row.amount=aid.amount
				row.aid_decision_date=exchange_date
				row.aid_no=aid.aid_no
				row.state=aid.state

# def get_item_details(args=None):
# 	item = frappe.db.sql("""select i.name, id.income_account,id.expense_account, id.default_warehouse, id.cost_center, id.project, id.project_activities 
# 			from `tabItem` i LEFT JOIN `tabItem Default` id ON i.name=id.parent and id.company=%s
# 			where i.name=%s
# 				and i.disabled=0
# 				and (i.end_of_life is null or i.end_of_life='0000-00-00' or i.end_of_life > %s)""",
# 			(args.get('company'), args.get('item_code'), nowdate()), as_dict = True)
# 	if not item:
# 			frappe.throw(_("Item {0} is not active or end of life has been reached").format(args.get("item_code")))

# 	return item[0]
						
# from erpnext.stock.get_item_details import get_valuation_rate
# from erpnext.accounts.utils import get_company_default

# @frappe.whitelist()
# def get_conversion_factor(item_code,uom):
# 	return frappe.db.get_value('UOM Conversion Detail', {'parent': item_code,'uom': uom}, 'conversion_factor')


# @frappe.whitelist()
# def get_item_detail(item_code, company, type,asset_category=""):
# 	item_dict = {}
# 	item_details = get_item_details({'item_code': item_code, 'company': company})
# 	item_dict['warehouse'] = item_details.get('default_warehouse')
# 	item_dict['income_account'] = (item_details.get("income_account") or get_item_group_defaults(item_code, company).get("income_account") or 
# 			get_company_default(company, "default_income_account") or frappe.get_cached_value('Company',  company, 
# 			"default_income_account"))
# 	item_dict['expense_account'] = (item_details.get("expense_account") or get_item_group_defaults(item_code, company).get("expense_account") or 
# 	get_company_default(company, "default_expense_account") or frappe.get_cached_value('Company',  company, 
# 	"default_expense_account"))
# 	# if type == 'Asset':
# 	# 	item_dict['asset_location'] = frappe.db.get_value('Asset', {'item_code': item_code}, 'location')
# 	item_dict['cost_center'] = item_details.get('cost_center')
# 	item_dict['project'] = item_details.get('project')
# 	item_dict['project_activities'] = item_details.get('project_activities')
# 	val = get_valuation_rate(item_code, company, item_dict['warehouse'])
# 	item_dict['valuation_rate'] = val['valuation_rate'] if val and 'valuation_rate' in val else 1

# 	warehouse_account = get_warehouse_account_map(company)
# 	stock_item = frappe.db.sql("""select name from `tabItem` where name in (%s) and is_stock_item=1""" , [item_code])

# 	if stock_item :
# 		item_dict['expense_account'] = warehouse_account[item_dict['warehouse']]["account"]
# 	elif asset_category:
# 		asset_account = get_asset_category_account(asset_category=asset_category, \
# 			fieldname='fixed_asset_account', company=company)
# 		item_dict['expense_account'] = asset_account

# 	return item_dict



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

