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

class BeneficiaryAidsEntry(Document):
	def validate(self):
		self.validate_item_code_and_warehouse()
		self.set_expense_account()
		self.set_against_expense_account()
		self.set_against_income_account()

	def on_submit(self):
		self.make_gl_entries()

	def on_cancel(self):
		self.make_gl_entries(cancel=True)

	def validate_item_code_and_warehouse(self):
		pass
	# 	for d in self.get('items'):
	# 		if not d.item_code:
	# 			frappe.msgprint(_("Item Code required at Row No {0}").format(d.idx), raise_exception=True)
	# 		if self.type != 'Cash' and not d.warehouse:
	# 			frappe.throw(_("Warehouse required at Row No {0}, please set default warehouse for the item {1} for the company {2}").
	# 				format(d.idx, d.item_code, self.company))
	
	def set_against_income_account(self):
		pass
	# 	against_acc = []
	# 	for d in self.get('items'):
	# 		if d.income_account and d.income_account not in against_acc:
	# 			against_acc.append(d.income_account)
	# 	self.against_income_account = ','.join(against_acc)

	def set_expense_account(self, for_validate=False):
		pass
	# 	warehouse_account = get_warehouse_account_map(self.company)
	# 	stock_items = self.get_stock_items()

	# 	for item in self.get("items"):
	# 		if not item.is_fixed_asset and item.item_code in stock_items:
	# 			item.expense_account = warehouse_account[item.warehouse]["account"]
	# 		elif item.is_fixed_asset and item.asset_category:
	# 			asset_account = get_asset_category_account(asset_category=item.asset_category, \
	# 				fieldname='fixed_asset_account', company=self.company)
	# 			item.expense_account = asset_account
	# 		elif not item.expense_account and for_validate:
	# 			throw(_("Expense account is mandatory for item {0}").format(item.item_code or item.item_name))

	def get_asset_items(self):
		pass
	# 	return [d.item_code for d in self.items if d.is_fixed_asset]


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
		self.make_beneficiary_gl_entry(gl_entries)
		
		if self.type == 'نقدي':
			self.make_cash_gl_entry(gl_entries)
		# # elif self.type=='عيني':
		# 	self.make_item_gl_entries(gl_entries)

		gl_entries = merge_similar_entries(gl_entries)

		return gl_entries

	def make_beneficiary_gl_entry(self, gl_entries):
		for row in self.get("beneficiaries"):
			gl_entries.append(
					self.get_gl_dict({
						"account": self.beneficiary_account,
						"party_type": "ٍSupplier",
						"party": row.beneficiary_name,
						"against": self.against_expense_account,
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
					"account": row.item_account,
					"party_type": "ٍSupplier",
					"party": self.customer,
					"against": self.against_income_account,
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
		pass
	# 	from erpnext.stock.stock_ledger import make_sl_entries
	# 	sl_entries = []
	# 	stock_items = self.get_stock_items()
	# 	for d in self.get('items'):
	# 		if d.item_code in stock_items and d.warehouse:
	# 			pr_qty = flt(d.qty) * flt(d.conversion_factor)
	# 			if pr_qty:
	# 				sle = frappe._dict({
	# 					"item_code": d.get("item_code", None),
	# 					"warehouse": d.get("warehouse", None),
	# 					"posting_date": self.posting_date,
	# 					"posting_time": self.posting_time,
	# 					'fiscal_year': get_fiscal_year(self.posting_date, company=self.company)[0],
	# 					"voucher_type": self.doctype,
	# 					"voucher_no": self.name,
	# 					"voucher_detail_no": d.name,
	# 					"actual_qty": flt(pr_qty),
	# 					"stock_uom": frappe.db.get_value("Item", d.get("item_code"), "stock_uom"),
	# 					"incoming_rate": pr_qty,
	# 					"company": self.company,
	# 					"batch_no": cstr(d.get("batch_no")).strip(),
	# 					"serial_no": d.get("serial_no"),
	# 					"project": self.project,
	# 					"is_cancelled": self.docstatus==2 and "Yes" or "No"
	# 				})
	# 				sl_entries.append(sle)

	# 	make_sl_entries(sl_entries, allow_negative_stock=allow_negative_stock,
	# 		via_landed_cost_voucher=via_landed_cost_voucher)

	def get_beneficiary_list(self):
		cond = 'where ben.status=%s and dis.state=0 and det.aid_no=dis.aid_no and det.type=%s '
		# dis.exchange_date IN (det.from_date,det.to_date) and
		filters=["جاري الصرف",self.type]
		if self.aid :
			cond += ' and det.aid=%s '
			filters.append(self.aid)	
		if self.project :
			cond += ' and det.project=%s '
			filters.append(self.project)
		if self.activity :
			cond += ' and det.activity=%s '
			filters.append(self.activity)
		if self.cost_center :
			cond += 'and det.cost_center=%s '
			filters.append(self.cost_center)
		if self.from_date :
			cond += 'and det.from_date >= %s '
			filters.append(self.from_date)
			cond += 'and dis.exchange_date IN %s '
			filters.append([self.from_date,self.to_date])
		if self.to_date :
			cond += 'and det.to_date <= %s '
			filters.append(self.to_date)
		"""
			Returns list of active beneficiary based on selected criteria
			and for which type exists
		"""
		# 	(select dis.exchange_date as exchange_date from `tabDisplay Aids` dis LEFT JOIN `tabAid Details` det 
		# LEFT JOIN `tabBeneficiary` ben ON ben.name = det.parent =dis.parent
		# where dis.state=1 and exchange_date IN (from_date,to_date) )
		return frappe.db.sql("""select beneficiary_name as beneficiary,ben.beneficiary_account,det.aid as aid,det.type as type,
		det.item_account as item_account,det.amount as amount,det.cost_center as cost_center 
		,det.project as project,det.activity as activity,det.from_date as from_date	,det.to_date as to_date
		,dis.exchange_date as exchange_date,dis.state as state,dis.aid_no,det.aid_no
		from `tabBeneficiary` ben
		LEFT JOIN  `tabDisplay Aids` dis 
	    ON ben.name=dis.parent
		LEFT JOIN `tabAid Details` det 	
		ON ben.name = det.parent
		
		{0}  """.format(cond), filters, as_dict=True)

	
	def fill_beneficiary(self):			
		beneficiaries = self.get_beneficiary_list()
		if not beneficiaries:
			frappe.throw(_("No beneficiaries for the mentioned type"))
		
		for d in beneficiaries:
			self.append('beneficiaries', d)
		
		self.number_of_beneficiaries = len(beneficiaries)
		

