from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document


def get_data():
	#if is_group:
		return {
			'fieldname': 'beneficiary',
			'transactions': [
				{
					'label': _('Beneficiary Family Member'),
					'items': ['Beneficiary Family Member']
				},
			]
		}