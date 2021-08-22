# Copyright (c) 2013, Baida and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe, erpnext
from erpnext import get_company_currency, get_default_company
from erpnext.accounts.report.utils import get_currency, convert_to_presentation_currency
from frappe.utils import getdate, cstr, flt, fmt_money
from frappe import _, _dict
from erpnext.accounts.utils import get_account_currency
from erpnext.accounts.report.financial_statements import get_cost_centers_with_children
from six import iteritems
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_accounting_dimensions, get_dimension_with_children
from collections import OrderedDict

def execute(filters=None):
	if not filters: filters = {}

	if not filters.get("date"):
		msgprint(_("Please select date"), raise_exception=1)
	
	columns = get_columns(filters)
	date = filters.get("date")
	
	columns, data = [], []
	return columns, data
