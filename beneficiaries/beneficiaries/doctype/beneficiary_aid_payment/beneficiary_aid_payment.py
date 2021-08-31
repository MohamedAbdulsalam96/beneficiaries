# -*- coding: utf-8 -*-
# Copyright (c) 2021, Baida and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.accounts.general_ledger import make_gl_entries, merge_similar_entries, delete_gl_entries
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from frappe.utils import cint, cstr, formatdate, flt, getdate, nowdate, get_link_to_form
from erpnext.controllers.buying_controller import BuyingController
from erpnext.stock import get_warehouse_account_map
from erpnext.assets.doctype.asset_category.asset_category import get_asset_category_account
from frappe import _, throw
from erpnext.accounts.utils import get_fiscal_year

class BeneficiaryAidPayment(BuyingController):
	def validate(self):
		pass

	def on_submit(self):
		self.make_gl_entries()
		if self.type == 'Material' and self.update_stock == 1:
			self.update_stock_ledger()
		# self.update_logs()

	def on_cancel(self):
		self.make_gl_entries(cancel=True)
		if self.type == 'Material' and self.update_stock == 1:
			self.update_stock_ledger()
		# self.cancel_logs_update()

	def onload(self):
			self.beneficiary_account=frappe.db.get_single_value('Beneficiary Settings', 'beneficiary_account')

	# def cancel_logs_update(self):
	# 	for item in self.get('items'):
	# 			filters=[item.beneficiary,item.aid_decision_date]
	# 			frappe.db.sql("""UPDATE `tabBeneficiary logs` set beneficiary_aid_payment=null where
	# 			 beneficiary=%s and exchange_date=%s """
	# 			,filters)

	# def update_logs(self):
	# 		for item in self.get('items'):
	# 			filters=['bb',item.beneficiary,item.aid_decision_date]
	# 			frappe.db.sql("""UPDATE `tabBeneficiary logs` set beneficiary_aid_payment=%s where
	# 			 beneficiary=%s and exchange_date=%s  and beneficiary_aid_payment=null"""
	# 			,filters)

	def fill_beneficiary(self):			
		beneficiaries = get_beneficiary_details(self.beneficiary,self.aid_decision_date,self.type)
		# frappe.msgprint(frappe.as_json(beneficiaries))
		if not beneficiaries:
			frappe.throw(_("No beneficiaries for the mentioned type"))
	
		for d in beneficiaries:
			
			self.append('items', d)
	
		self.number_of_beneficiaries = len(beneficiaries)

	

	def validate_item_code_and_warehouse(self):
		for d in self.get('items'):
			if not d.item_code:
				frappe.msgprint(_("Item Code required at Row No {0}").format(d.idx))
			if not d.income_account:
				frappe.msgprint(_("income_account required at Row No {0}").format(d.idx))
			if (self.type != 'Cash' or self.type!= 'Cash Material') and  not d.expense_account:
				frappe.throw(_("expense_account required at Row No {0}").format(d.idx))
			if ( self.type != 'Cash' or self.type!= 'Cash Material') and not d.warehouse:
				frappe.throw(_("Warehouse required at Row No {0}").format(d.idx))

	

	def make_gl_entries(self, cancel = False):
		# if not self.total:
		# 	return
		gl_entries = self.get_gl_entries()

		if gl_entries:
			make_gl_entries(gl_entries,  cancel= cancel)

	def get_gl_entries(self, warehouse_account=None):
		gl_entries = []
	
		# self.make_income_gl_entries(gl_entries)
		
		if self.type == 'Cash'  or self.type!= 'Cash Material':
			self.make_beneficiary_gl_entry(gl_entries)
			# self.make_cash_gl_entry(gl_entries)
		elif self.type=='Material':
		   
			self.make_material_beneficiary_gl_entry(gl_entries)
			# self.make_item_gl_entries(gl_entries)
			


		gl_entries = merge_similar_entries(gl_entries)

		return gl_entries

	def make_beneficiary_gl_entry(self, gl_entries):
			for row in self.get("items"):
				gl_entries.append(
						self.get_gl_dict({
							"posting_date":self.posting_date,
							"account": row.paid_from,
							"party_type": "Beneficiary",
							"party": row.beneficiary,						
							"debit": row.amount,
							"debit_in_account_currency": row.amount,
							"against_voucher": self.name,
							"against_voucher_type": self.doctype,
							"remarks": self.get("remarks") or _("Accounting Entry for Beneficiary"),
							"cost_center": row.cost_center,
							"project": row.project
						}, item=self))

				gl_entries.append(
					self.get_gl_dict({
						"posting_date":self.posting_date,
						"account": self.paid_to,
						"credit": row.amount,
						"credit_in_account_currency": row.amount,
						"against_voucher": self.name,
						"against_voucher_type": self.doctype,
						"remarks": self.get("remarks") or _("Accounting Entry for Expenses"),
						"cost_center": row.cost_center,
						"project": row.project
					}, item=self))

	def make_material_beneficiary_gl_entry(self, gl_entries):
			for row in self.get("items"):
				expense_account=(row.get("expense_account") or
				item_group_defaults.get("expense_account") or
				frappe.get_cached_value('Company',  self.company,  "default_expense_account"))
				gl_entries.append(
						self.get_gl_dict({
							"posting_date":self.posting_date,
							"account": row.paid_from,
							"party_type": "Beneficiary",
							"party": row.beneficiary,						
							"debit": row.amount,
							"debit_in_account_currency": row.amount,
							"against_voucher": self.name,
							"against_voucher_type": self.doctype,
							"remarks": self.get("remarks") or _("Accounting Entry for Beneficiary"),
							"cost_center": row.cost_center,
							"project": row.project
						}, item=self))

				gl_entries.append(
					self.get_gl_dict({
						"posting_date":self.posting_date,
						"account": row.expense_account,
						"credit": row.amount,
						"credit_in_account_currency": row.amount,
						"against_voucher": self.name,
						"against_voucher_type": self.doctype,
						"remarks": self.get("remarks") or _("Accounting Entry for Expenses"),
						"cost_center": row.cost_center,
						"project": row.project
					}, item=self))
	
	
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

	def get_asset_items(self):
		return [d.item_code for d in self.items if d.is_fixed_asset]


	def update_stock_ledger(self, allow_negative_stock=False, via_landed_cost_voucher=False):
		sl_entries = []
		stock_items = self.get_stock_items()
		for d in self.get('items'):
			if d.item_code in stock_items and d.warehouse:
				# pr_qty = flt(d.qty) * flt(d.conversion_factor)

				val_rate_db_precision = 6 if cint(self.precision("valuation_rate", d)) <= 6 else 9
				incoming_rate = flt(d.valuation_rate, val_rate_db_precision)
				# if pr_qty:
				sle = self.get_sl_entries(d,{
						"item_code": d.get("item_code", None),
						"warehouse": d.get("warehouse", None),
						"posting_date": self.posting_date,
						"posting_time": self.posting_time,
						'fiscal_year': get_fiscal_year(self.posting_date, company=self.company)[0],
						"voucher_type": self.doctype,
						"voucher_no": self.name,
						"voucher_detail_no": d.name,
						"actual_qty": -d.qty,
						"stock_uom": frappe.db.get_value("Item", d.get("item_code"), "stock_uom"),
						"outgoing_rate": incoming_rate,
						"company": self.company,
						"batch_no": cstr(d.get("batch_no")).strip(),
						"serial_no": cstr(d.serial_no).strip(),
						"is_cancelled": self.docstatus==2 and "Yes" or "No"
					})
				sl_entries.append(sle)

		self.make_sl_entries_for_supplier_warehouse(sl_entries)
		self.make_sl_entries(sl_entries, allow_negative_stock=allow_negative_stock,
			via_landed_cost_voucher=via_landed_cost_voucher)

	def make_item_gl_entries(self, gl_entries):
			for item in self.get("items"):
				if flt(item.amount):
					gl_entries.append(
						self.get_gl_dict({
								"account": item.expense_account,
								"against": self.paid_from,
								"debit": self.total,
								"remarks": self.get("remarks") or _("Accounting Entry for Stock"),
								"cost_center": item.cost_center,
								"project": item.project,
							}, item=item)
						)
		
	

def get_item_details(args=None):
	item = frappe.db.sql("""select i.name, id.income_account, id.default_warehouse, id.cost_center, id.project, id.project_activities 
			from `tabItem` i LEFT JOIN `tabItem Default` id ON i.name=id.parent and id.company=%s
			where i.name=%s
				and i.disabled=0
				and (i.end_of_life is null or i.end_of_life='0000-00-00' or i.end_of_life > %s)""",
			(args.get('company'), args.get('item_code'), nowdate()), as_dict = True)
	if not item:
			frappe.throw(_("Item {0} is not active or end of life has been reached").format(args.get("item_code")))

	return item[0]

@frappe.whitelist()
def get_beneficiary_details(beneficiary,aid_decision_date,type1):
	filters=[type1,aid_decision_date]
	cond=''
	if beneficiary:
		cond = 'and ben.beneficiary_name=%s '
		filters.append(beneficiary)
	
	
	x= frappe.db.sql("""select ben.beneficiary_name as beneficiary ,det.item_code ,det.aid_decision_date,det.amount,det.warehouse ,det.qty,det.valuation_rate 
		,det.item_name,det.type,det.rate,det.income_account,det.expense_account
		from `tabBeneficiary` ben
		
		LEFT JOIN `tabAids Entry Details` det 
		ON ben.name = det.beneficiary

		where det.type=%s and det.aid_decision_date=%s  {0}
	
		GROUP BY ben.name, det.aid_decision_date,det.amount,det.item_code
		  """.format(cond), filters, as_dict=True)
	# frappe.msgprint(frappe.as_json(x))
	return x
@frappe.whitelist()
def get_conversion_factor(item_code, uom):
	return frappe.db.get_value('UOM Conversion Detail', {'parent': item_code,'uom': uom}, 'conversion_factor')


from erpnext.stock.get_item_details import get_valuation_rate
from erpnext.accounts.utils import get_company_default

@frappe.whitelist()
def get_item_detail(item_code, is_fixed_asset,  company, type):
	item_dict = {}
	item_details = get_item_details({'item_code': item_code, 'company': company})
	item_dict['warehouse'] = item_details.get('default_warehouse')
	item_dict['income_account'] = (item_details.get("income_account") or get_item_group_defaults(item_code, company).get("income_account") or 
			get_company_default(company, "default_income_account") or frappe.get_cached_value('Company',  company, 
			"default_income_account"))
	item_dict['expense_account'] = (item_details.get("expense_account") or get_item_group_defaults(item_code, company).get("expense_account") or 
			get_company_default(company, "default_expense_account") or frappe.get_cached_value('Company',  company, 
			"default_expense_account"))
	# if type == 'Asset':
	# 	item_dict['asset_location'] = frappe.db.get_value('Asset', {'item_code': item_code}, 'location')
	item_dict['cost_center'] = item_details.get('cost_center')
	item_dict['project'] = item_details.get('project')
	item_dict['project_activities'] = item_details.get('project_activities')
	val = get_valuation_rate(item_code, company, item_dict['warehouse'])
	item_dict['valuation_rate'] = val['valuation_rate'] if val and 'valuation_rate' in val else 1

	warehouse_account = get_warehouse_account_map(company)
	stock_item = frappe.db.sql("""select name from `tabItem` where name in (%s) and is_stock_item=1""" , [item_code])

	if stock_item and is_fixed_asset == '0':
		item_dict['expense_account'] = warehouse_account[item_dict['warehouse']]["account"]


	return item_dict


@frappe.whitelist()
def get_payment_account(mode_of_payment, company):
	account = frappe.db.get_value("Mode of Payment Account",
		{"parent": mode_of_payment, "company": company}, "default_account")
	if not account:
		frappe.throw(_("Please set default account in Mode of Payment {0}")
			.format(mode_of_payment))

	return {
		"account": account,
		"account_currency": frappe.db.get_value("Account", {"name": account}, "account_currency")
	}
