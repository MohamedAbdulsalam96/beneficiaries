from __future__ import unicode_literals
from frappe import _


def get_data():
	return {
		'fieldname': 'beneficiary',
		'transactions': [
			{
				'label': _('Beneficiary Return'),
				'items': ['Beneficiary Return']
			},
	
			{
				'label': _('Beneficiary logs'),
				'items': ['Beneficiary logs']
			},
		
		 ]
		
	}