from __future__ import unicode_literals
from frappe import _


def get_data():
	return {
		'fieldname': 'beneficiary_request',
		'transactions': [
			{
				'label': _('Beneficiary Request'),
				'items': ['Beneficiary']
			},
		]
	}