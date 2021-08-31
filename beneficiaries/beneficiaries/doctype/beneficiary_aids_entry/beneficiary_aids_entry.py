# -*- coding: utf-8 -*-
# Copyright (c) 2021, Baida and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.accounts.general_ledger import make_gl_entries, merge_similar_entries, delete_gl_entries
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from frappe.utils import cint, cstr, formatdate, flt, getdate, nowdate, get_link_to_form
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.stock import get_warehouse_account_map
from erpnext.assets.doctype.asset_category.asset_category import get_asset_category_account
from frappe import _, throw
from erpnext.accounts.utils import get_fiscal_year

class BeneficiaryAidsEntry(AccountsController):
	def get_ben_acc (self):
		self.beneficiary_account=frappe.db.get_single_value('Beneficiary Settings', 'beneficiary_account')
	def validate(self):
		# if self.type=='Material':
		pass

	def on_submit(self):
		self.make_gl_entries()
		self.update_deserve_check()
		# self.create_log()

	def on_cancel(self):
		self.make_gl_entries(cancel=True)
		# self.delete_log()

	def get_beneficiary_list(self):
		cond = 'where benef.status=%s and dis.state=0 and det.aid_no=dis.aid_no and det.type=%s '
		# dis.exchange_date IN (det.from_date,det.to_date) and
		filters=["In Progress",self.type]
		if self.aid_type :
			cond += ' and det.aid_type=%s '
			filters.append(self.aid_type)
		if self.from_date :
			cond += 'and det.from_date >= %s '
			filters.append(self.from_date)
			cond += 'and dis.aid_decision_date IN %s '
			filters.append([self.from_date,self.to_date])
		if self.to_date :
			cond += 'and det.to_date <= %s '
			filters.append(self.to_date)
		"""
			Returns list of active beneficiary based on selected criteria
			and for which type exists
		"""

		return frappe.db.sql("""select beneficiary as beneficiary,benef.beneficiary_account,benef.beneficiary_name,
		det.amount,det.type,
		det.from_date ,det.to_date,det.aid_type
		,dis.aid_decision_date,dis.state,dis.aid_no,det.aid_no

		from `tabBeneficiary Aid` ben
		LEFT JOIN  `tabDisplay Aids` dis 
	    ON ben.name=dis.parent

		LEFT JOIN  `tabBeneficiary` benef 
	    ON ben.beneficiary=benef.beneficiary_name

		LEFT JOIN `tabAid Details` det 	
		ON ben.name = det.parent
		
		{0}  """.format(cond), filters, as_dict=True)

	def get_beneficiaries(self):
		filters=[self.type,self.from_date]
		x= frappe.db.sql("""select ben.beneficiary
		from `tabBeneficiary Aid` ben
		LEFT JOIN  `tabAid Details` det 
		ON ben.name = det.parent

		LEFT JOIN `tabDisplay Aids` dis 
	    ON ben.name=dis.parent

		where dis.state=0 and det.type=%s and dis.aid_decision_date=%s  and det.aid_no=dis.aid_no
	
		GROUP BY det.parent, dis.aid_decision_date,det.amount,det.item_code
		  """, filters, as_dict=True)
		# frappe.msgprint(frappe.as_json(x))
		return x

	def fill_material_aid(self):
		beneficiaries_list=[]
		for ben in self.get('ben_mat'):
			for aid in self.get('aid_material'):
				aids={'beneficiary' : ben.beneficiary, 'item_code':aid.item_code, 'qty':aid.qty}
				beneficiaries_list.append(aids)
		# frappe.msgprint(frappe.as_json(beneficiaries_list))
		return beneficiaries_list

	def fill_beneficiary(self):	
		# m=self.get_beneficiaries()
		# frappe.msgprint(frappe.as_json(m))
		if self.type=="Cash" or self.type=="Cash Material":		
			beneficiaries = self.get_beneficiary_list()
			# frappe.msgprint(frappe.as_json(beneficiaries))
			if not beneficiaries:
				frappe.throw(_("No beneficiaries for the mentioned type"))
			for d in beneficiaries:
				row=self.append('items', {})
				row.beneficiary=d.beneficiary
				row.aid_decision_date=d.aid_decision_date
				row.aid_type=d.aid_type
				row.amount =d.amount 
				row.type=d.type
			
		elif self.type=="Material":
			beneficiaries=self.fill_material_aid()		
			for d in beneficiaries:
				row = self.append('items', {})
				row.beneficiary=d['beneficiary']
				row.type=self.type
				row.aid_decision_date=self.from_date
				row.item_code=d['item_code']
				row.qty=d['qty']

		self.number_of_beneficiaries = len(beneficiaries)
			

			


	def update_deserve_check(self):
		for item in self.get('items'):
			filters=[item.beneficiary,item.aid_decision_date,item.type]
			frappe.db.sql("""UPDATE `tabDisplay Aids` set state=1 where parent=%s and aid_decision_date=%s and type=%s """
			 ,filters)
			
		

	def validate_item_code_and_warehouse(self):
	
		for d in self.get('items'):
			if not d.item_code:
				frappe.msgprint(_("Item Code required at Row No {0}").format(d.idx), raise_exception=True)
			if (self.type != 'Cash' or self.type=='Cash Material') and not d.warehouse:
				frappe.throw(_("Warehouse required at Row No {0}, please set default warehouse for the item {1} for the company {2}").
					format(d.idx, d.item_code, self.company))
	

	def get_asset_items(self):
	
		return [d.item_code for d in self.items if d.is_fixed_asset]



	def make_gl_entries(self, cancel = False):
		# if not self.total:
		# 	return
		gl_entries = self.get_gl_entries()

		if gl_entries:
			make_gl_entries(gl_entries,  cancel= cancel)

	def get_gl_entries(self, warehouse_account=None):
		gl_entries = []
		if self.type == 'Cash' or self.type=='Cash Material':
			self.make_beneficiary_gl_entry(gl_entries)
			# self.make_cash_gl_entry(gl_entries)
		elif self.type=='Material':
			
			self.make_beneficiary_stock_gl_entry(gl_entries)
			self.update_stock_ledger()

		
		# self.make_beneficiary_gl_entry(gl_entries)
		
		

		gl_entries = merge_similar_entries(gl_entries)

		return gl_entries

	# def get_expenses_account(self,code):
	# 	account= frappe.db.sql("""select def.expense_account
	# 	from `tabItem` item
	# 	LEFT JOIN  `tabItem Default` def 
	#     ON item.name=def.parent
	# 	where item.item_code=%s""",{ code}, as_dict=True)
	# 	if not account:
	# 		  account=frappe.db.sql("""select def.expense_account from `tabItem Group` item
	# 	LEFT JOIN  `tabItem Default` def ON item.name=def.parent where item.item_code=%s """,{ code}, as_dict=True)
	# 	if not account:
	# 		 account=frappe.db.sql("""select default_expense_account from `tabCompany` """, as_dict=True)
	# 	if not account:
	# 		frappe.msgprint("You should to Enter Default expenses account in item default ")

	def make_beneficiary_stock_gl_entry(self, gl_entries):
		for row in self.get("items"):
			gl_entries.append(
					self.get_gl_dict({
						"posting_date":self.posting_date,
						"account": self.beneficiary_account,
						"party_type": "Beneficiary",
						"party": row.beneficiary,						
						"credit":row.amount,
						"credit_in_account_currency":row.amount,
						"against_voucher": self.name,
						"against_voucher_type": self.doctype,
						"remarks": self.get("remarks") or _("Accounting Entry for Stock Entry To Beneficiary"),
						"cost_center": row.cost_center,
						"project": row.project
					}, item=self))

			gl_entries.append(
				self.get_gl_dict({
					"posting_date":self.posting_date,
					"account": row.expense_account,
					"debit": row.amount,
					"debit_in_account_currency": row.amount,
					"against_voucher": self.name,
					"against_voucher_type": self.doctype,
					"remarks": self.get("remarks") or _("Accounting Entry for Stock Entry From Expenses"),
					"cost_center": row.cost_center,
					"project": row.project
				}, item=self))

	def make_beneficiary_gl_entry(self, gl_entries):
		for row in self.get("items"):
			gl_entries.append(
					self.get_gl_dict({
						"posting_date":self.posting_date,
						"account": self.beneficiary_account,
						"party_type": "Beneficiary",
						"party": row.beneficiary,						
						"credit": row.amount,
						"credit_in_account_currency": row.amount,
						"against_voucher": self.name,
						"against_voucher_type": self.doctype,
						"remarks": self.get("remarks") or _("Accounting Entry for Funder Paid From"),
						"cost_center": row.cost_center,
						"project": row.project
					}, item=self))

			gl_entries.append(
				self.get_gl_dict({
					"posting_date":self.posting_date,
					"account": self.account_paid_from,
					"debit": row.amount,
					"debit_in_account_currency": row.amount,
					"against_voucher": self.name,
					"against_voucher_type": self.doctype,
					"remarks": self.get("remarks") or _("Accounting Entry for Funder To"),
					"cost_center": self.cost_center,
					"project": row.project
				}, item=self))


	def update_stock_ledger(self, allow_negative_stock=False, via_landed_cost_voucher=False):
		from erpnext.stock.stock_ledger import make_sl_entries
		sl_entries = []
		stock_items = self.get_stock_items()
		for d in self.get('items'):
			if d.item_code in stock_items and d.warehouse:
				pr_qty = flt(d.qty) * flt(d.conversion_factor)

				val_rate_db_precision = 6 if cint(self.precision("valuation_rate", d)) <= 6 else 9
				if pr_qty:
					sle = frappe._dict({
						"item_code": d.item_code,
						"warehouse": d.warehouse,
						"posting_date": self.posting_date,
						"posting_time": self.posting_time,
						'fiscal_year': get_fiscal_year(self.posting_date, company=self.company)[0],
						"voucher_type": self.doctype,
						"voucher_no": self.name,
						"voucher_detail_no": d.name,
						"actual_qty": flt(pr_qty),
						"stock_uom": frappe.db.get_value("Item", d.get("item_code"), "stock_uom"),
						"incoming_rate": pr_qty,
						"company": self.company,
						 "batch_no": cstr(d.get("batch_no")).strip(),
						 "serial_no": d.get("serial_no"),
						"project": self.project,
						"is_cancelled": self.docstatus==2 and "Yes" or "No"
					})
					sl_entries.append(sle)

		make_sl_entries(sl_entries, allow_negative_stock=allow_negative_stock,
			via_landed_cost_voucher=via_landed_cost_voucher)

	

	def get_asset_items(self):
		return [d.item_code for d in self.items if d.is_fixed_asset]
	def update_valuation_rate(self, parentfield):
		stock_and_asset_items = self.get_stock_items() + self.get_asset_items()
		# frappe.msgprint(frappe.as_json(stock_and_asset_items))

		for i, item in enumerate(self.get(parentfield)):
			if item.item_code and item.qty and item.item_code in stock_and_asset_items:

				self.round_floats_in(item)
				if flt(item.conversion_factor)==0.0:
					item.conversion_factor = get_conversion_factor(item.item_code, item.uom).get("conversion_factor") or 1.0

				qty_in_stock_uom = flt(item.qty * item.conversion_factor)

				item.valuation_rate = ((item.amount) / qty_in_stock_uom)
			else:
				item.valuation_rate = 0.0


def get_item_details(args=None):
	item = frappe.db.sql("""select i.name, id.income_account,id.expense_account, id.default_warehouse, id.cost_center, id.project, id.project_activities 
			from `tabItem` i LEFT JOIN `tabItem Default` id ON i.name=id.parent and id.company=%s
			where i.name=%s
				and i.disabled=0
				and (i.end_of_life is null or i.end_of_life='0000-00-00' or i.end_of_life > %s)""",
			(args.get('company'), args.get('item_code'), nowdate()), as_dict = True)
	if not item:
			frappe.throw(_("Item {0} is not active or end of life has been reached").format(args.get("item_code")))

	return item[0]
		

	


from erpnext.stock.get_item_details import get_valuation_rate
from erpnext.accounts.utils import get_company_default

@frappe.whitelist()
def get_conversion_factor(item_code,uom):
	return frappe.db.get_value('UOM Conversion Detail', {'parent': item_code,'uom': uom}, 'conversion_factor')


@frappe.whitelist()
def get_item_detail(company, type,item_code="", is_fixed_asset=0,asset_category=""):
	item_dict = {}
	if type=="Material":
		item_details = get_item_details({'item_code': item_code, 'company': company})
		item_dict['warehouse'] = item_details.get('default_warehouse')
		item_dict['income_account'] = (item_details.get("income_account") or get_item_group_defaults(item_code, company).get("income_account") or 
				get_company_default(company, "default_income_account") or frappe.get_cached_value('Company',  company, 
				"default_income_account"))
		# if type == 'Asset':
		# 	item_dict['asset_location'] = frappe.db.get_value('Asset', {'item_code': item_code}, 'location')
		item_dict['cost_center'] = item_details.get('cost_center')
		item_dict['project'] = item_details.get('project')
		item_dict['project_activities'] = item_details.get('project_activities')
		val = get_valuation_rate(item_code, company, item_dict['warehouse'])
		item_dict['valuation_rate'] = val['valuation_rate'] if val and 'valuation_rate' in val else 1
		item_dict['expense_account'] = (item_details.get("expense_account") or get_item_group_defaults(item_code, company).get("expense_account") or 
				get_company_default(company, "default_expense_account") or frappe.get_cached_value('Company',  company, 
				"default_expense_account"))
		warehouse_account = get_warehouse_account_map(company)
		stock_item = frappe.db.sql("""select name from `tabItem` where name in (%s) and is_stock_item=1""" , [item_code])

		if stock_item and is_fixed_asset == '0':
			item_dict['expense_account'] = warehouse_account[item_dict['warehouse']]["account"]
		elif is_fixed_asset == '1' and asset_category:
			asset_account = get_asset_category_account(asset_category=asset_category, \
				fieldname='fixed_asset_account', company=company)
			item_dict['expense_account'] = asset_account

	return item_dict
