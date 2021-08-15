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
	def validate(self):
	
		if self.type=='Material':
			self.validate_item_code_and_warehouse()
			self.set_expense_account()
			self.set_against_expense_account()
			self.set_against_income_account()
			# self.update_valuation_rate("items")

	def on_submit(self):
		self.make_gl_entries()
		self.update_deserve_check()
		self.create_log()

	def on_cancel(self):
		self.make_gl_entries(cancel=True)
		self.delete_log()

	def create_log(self):
		for item in self.get('items'):
			log = frappe.new_doc('Beneficiary logs')
			log.beneficiary = item.beneficiary
			log.exchange_date = item.exchange_date
			log.type = item.type
			log.amount = item.amount
			log.item_code = item.item_code
			log.qty=item.qty
			log.warehouse=item.warehouse
			log.beneficiary_account=item.beneficiary_account
			log.aids_account=item.item_account
			log.income_account=item.income_account
			log.expense_account=item.expense_account
			log.beneficiary_aids_entry= self.name
			log.insert()
		frappe.msgprint('Beneficiary log Inserted Done :)')
			
	def delete_log(self):
		for item in self.get('items'):
			filters=[item.beneficiary,item.exchange_date,item.item_code,item.type,item.amount]
			frappe.db.sql("""delete from `tabBeneficiary logs` where beneficiary=%s and exchange_date=%s and item_code=%s and type=%s and amount=%s"""
			 ,filters)
		



	def get_beneficiary_list(self):
		cond = 'where ben.status=%s and dis.state=0 and det.aid_no=dis.aid_no and det.type=%s '
		# dis.exchange_date IN (det.from_date,det.to_date) and
		filters=["In Progress",self.type]
		if self.aid :
			cond += ' and det.item_code=%s '
			filters.append(self.aid)	
		if self.project :
			cond += ' and det.project=%s '
			filters.append(self.project)
		if self.aid_type :
			cond += ' and det.aid_type=%s '
			filters.append(self.aid_type)
		if self.activity :
			cond += ' and det.activity=%s '
			filters.append(self.activity)
		if self.cost_center :
			cond += 'and det.cost_center=%s '
			filters.append(self.cost_center)
		if self.from_date :
			cond += 'and det.from_date >= %s '
			filters.append(self.from_date)
			# cond += 'and dis.exchange_date IN %s '
			# filters.append([self.from_date,self.to_date])
		if self.to_date :
			cond += 'and det.to_date <= %s '
			filters.append(self.to_date)
		"""
			Returns list of active beneficiary based on selected criteria
			and for which type exists
		"""

		return frappe.db.sql("""select beneficiary_name as beneficiary,ben.beneficiary_account,det.item_code ,det.type ,
		det.item_account ,det.amount,det.cost_center,det.warehouse ,det.qty ,det.aid_type
		,det.project ,det.activity ,det.from_date ,det.to_date ,det.asset_category 
		,dis.exchange_date,dis.state,dis.aid_no,det.aid_no,det.uom,det.rate,det.valuation_rate,det.conversion_factor,
		det.stock_qty,det.uom, det.income_account,det.expense_account
		from `tabBeneficiary` ben
		LEFT JOIN  `tabDisplay Aids` dis 
	    ON ben.name=dis.parent
		LEFT JOIN `tabAid Details` det 	
		ON ben.name = det.parent
		
		{0}  """.format(cond), filters, as_dict=True)

	
	def fill_beneficiary(self):			
		beneficiaries = self.get_beneficiary_list()
		frappe.msgprint(frappe.as_json(beneficiaries))
		if not beneficiaries:
			frappe.throw(_("No beneficiaries for the mentioned type"))
		item_code=[]
		for d in beneficiaries:
			# frappe.msgprint(d.warehouse)
			self.append('items', d)
			# item_code.append(row.item_code)
			# row.valuation_rate=frappe.db.get_value("Item", row.get("item_code"), "valuation_rate")
		self.number_of_beneficiaries = len(beneficiaries)
		# frappe.msgprint(item_code)
		# return item_code


	def update_deserve_check(self):
		for item in self.get('items'):
			filters=[item.beneficiary,item.exchange_date,item.item_code,item.type]
			frappe.db.sql("""UPDATE `tabDisplay Aids` set state=1 where parent=%s and exchange_date=%s and item_code=%s and type=%s"""
			 ,filters)
		

	def validate_item_code_and_warehouse(self):
	
		for d in self.get('items'):
			if not d.item_code:
				frappe.msgprint(_("Item Code required at Row No {0}").format(d.idx), raise_exception=True)
			if self.type != 'Cash' and not d.warehouse:
				frappe.throw(_("Warehouse required at Row No {0}, please set default warehouse for the item {1} for the company {2}").
					format(d.idx, d.item_code, self.company))
	
	def set_against_income_account(self):
	
		against_acc = []
		for d in self.get('items'):
			if d.income_account and d.income_account not in against_acc:
				against_acc.append(d.income_account)
		self.against_income_account = ','.join(against_acc)

	def set_expense_account(self, for_validate=False):
		
		warehouse_account = get_warehouse_account_map(self.company)
		stock_items = self.get_stock_items()

		for item in self.get("items"):
			if not item.is_fixed_asset and item.item_code in stock_items:
				item.expense_account = warehouse_account[item.warehouse]["account"]
			elif item.is_fixed_asset and item.asset_category:
				asset_account = get_asset_category_account(asset_category=item.asset_category, \
					fieldname='fixed_asset_account', company=self.company)
				item.expense_account = asset_account
			elif not item.expense_account and for_validate:
				throw(_("Expense account is mandatory for item {0}").format(item.item_code or item.item_name))

	def get_asset_items(self):
	
		return [d.item_code for d in self.items if d.is_fixed_asset]


	def set_against_expense_account(self):
		pass
		
	# 	if self.type == 'Cash':
	# 		self.against_expense_account = self.paid_to
	# 	else:
	# 		against_accounts = []
	# 		for item in self.get("items"):
	# 			if item.expense_account and (item.expense_account not in against_accounts):
	# 				against_accounts.append(item.expense_account)
	# 				self.against_expense_account = ",".join(against_accounts)


	def make_gl_entries(self, cancel = False):
		# if not self.total:
		# 	return
		gl_entries = self.get_gl_entries()

		if gl_entries:
			make_gl_entries(gl_entries,  cancel= cancel)

	def get_gl_entries(self, warehouse_account=None):
		gl_entries = []
		if self.type == 'Cash':
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
						"account": row.beneficiary_account,
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
						"account": row.beneficiary_account,
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
					"account": row.item_account,
					"debit": row.amount,
					"debit_in_account_currency": row.amount,
					"against_voucher": self.name,
					"against_voucher_type": self.doctype,
					"remarks": self.get("remarks") or _("Accounting Entry for Funder To"),
					"cost_center": row.cost_center,
					"project": row.project
				}, item=self))

	def make_income_gl_entries(self, gl_entries):
		pass
	# 	for item in self.get("items"):
	# 			gl_entries.append(
	# 			self.get_gl_dict({
	# 				"account": item.income_account,
	# 				"against": self.customer,
	# 				"credit": self.total,
	# 				"credit_in_account_currency": self.total,
	# 				"remarks": self.get("remarks") or _("Accounting Entry for Income"),
	# 				"cost_center": item.cost_center,
	# 				"project": item.project or self.project
	# 			}, item=item)
	# 			)

	def make_cash_gl_entry(self, gl_entries):
		pass
	# 		gl_entries.append(
	# 			self.get_gl_dict({
	# 				"account": self.paid_to,
	# 				"against": self.paid_from,
	# 				"debit": self.total,
	# 				"debit_in_account_currency": self.total,
	# 				"against_voucher": self.name,
	# 				"against_voucher_type": self.doctype,
	# 				"remarks": self.get("remarks") or _("Accounting Entry for Cash & Bank"),
	# 				"cost_center": self.cost_center,
	# 				"project": self.project
	# 			}, item=self))

	def make_item_gl_entries(self, gl_entries):
		pass
		
	# 	for item in self.get("items"):
	# 		if flt(item.amount):
	# 			gl_entries.append(
	# 				self.get_gl_dict({
	# 						"account": item.expense_account,
	# 						"against": self.paid_from,
	# 						"debit": self.total,
	# 						"remarks": self.get("remarks") or _("Accounting Entry for Stock"),
	# 						"cost_center": item.cost_center,
	# 						"project": item.project or self.project
	# 					}, item=item)
	# 				)
	
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
def get_item_detail(item_code, is_fixed_asset, company, type,asset_category=""):
	item_dict = {}
	item_details = get_item_details({'item_code': item_code, 'company': company})
	item_dict['warehouse'] = item_details.get('default_warehouse')
	item_dict['income_account'] = (item_details.get("income_account") or get_item_group_defaults(item_code, company).get("income_account") or 
			get_company_default(company, "default_income_account") or frappe.get_cached_value('Company',  company, 
			"default_income_account"))
	if type == 'Asset':
		item_dict['asset_location'] = frappe.db.get_value('Asset', {'item_code': item_code}, 'location')
	item_dict['cost_center'] = item_details.get('cost_center')
	item_dict['project'] = item_details.get('project')
	item_dict['project_activities'] = item_details.get('project_activities')
	val = get_valuation_rate(item_code, company, item_dict['warehouse'])
	item_dict['valuation_rate'] = val['valuation_rate'] if val and 'valuation_rate' in val else 1

	warehouse_account = get_warehouse_account_map(company)
	stock_item = frappe.db.sql("""select name from `tabItem` where name in (%s) and is_stock_item=1""" , [item_code])

	if stock_item and is_fixed_asset == '0':
		item_dict['expense_account'] = warehouse_account[item_dict['warehouse']]["account"]
	elif is_fixed_asset == '1' and asset_category:
		asset_account = get_asset_category_account(asset_category=asset_category, \
			fieldname='fixed_asset_account', company=company)
		item_dict['expense_account'] = asset_account

	return item_dict
