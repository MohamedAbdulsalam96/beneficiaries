from __future__ import unicode_literals
from frappe import _


def get_data():
	return {
		'fieldname': 'beneficiary',
			'internal_links': {
			'Beneficiary Aids Entry': ['items', 'beneficiary_aids_entry']
		},
		'transactions': [
			
	
			{
				'label': _('Beneficiary Aid'),
				'items': ['Beneficiary Aid']
			},
				{
				'label': _('Beneficiary Renewal'),
				'items': ['Beneficiary Renewal']
			},
		
		
		],
		
		
	}