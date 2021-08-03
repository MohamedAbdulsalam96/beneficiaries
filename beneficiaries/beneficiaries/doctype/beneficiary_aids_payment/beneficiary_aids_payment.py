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

class BeneficiaryAidsPayment(AccountsController):
	def validate(self):
		self.validate_item_code_and_warehouse()
		self.set_expense_account()
		self.set_against_expense_account()
		self.set_against_income_account()


	def validate_item_code_and_warehouse(self):
		pass
	def set_expense_account(self):
		pass
	def set_against_expense_account(self):
		pass
	def set_against_income_account(self):
		pass
	
	def on_submit(self):
		self.make_gl_entries()

	def on_cancel(self):
		self.make_gl_entries(cancel=True)
	def make_gl_entries(self, cancel = False):
			# if not self.total:
			# 	return
			gl_entries = self.get_gl_entries()

			if gl_entries:
				make_gl_entries(gl_entries,  cancel= cancel)

	def get_gl_entries(self, warehouse_account=None):
		gl_entries = []
		self.make_beneficiary_gl_entry(gl_entries)
		# gl_entries = merge_similar_entries(gl_entries)
		return gl_entries

	def make_beneficiary_gl_entry(self, gl_entries):
		gl_entries.append(
				self.get_gl_dict({
				"posting_date":self.posting_date,
				"account": self.from_account,
				"credit": self.amount,
				"credit_in_account_currency": self.amount,
				"against_voucher": self.name,
				"against_voucher_type": self.doctype,
				"remarks": self.get("remarks") or _("Accounting Entry for Funder To"),
					
				}, item=self))

		gl_entries.append(
			self.get_gl_dict({
				"posting_date":self.posting_date,
				"account": self.beneficiary_account,
				"party_type": "Beneficiary",
				"party": self.beneficiary,						
				"debit": self.amount,
				"debit_in_account_currency": self.amount,
				"against_voucher": self.name,
				"against_voucher_type": self.doctype,
				"remarks": self.get("remarks") or _("Accounting Entry for Funder Paid From"),
			}, item=self))

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