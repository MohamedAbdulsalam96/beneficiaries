from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Initialization"),
			"items":
			 [
				 {
					"type": "doctype",
					"name": "Beneficiary Settings",
					"description":_("Beneficiary Settings"),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Basic Need",
					"description":_("Basic Need"),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Additional Need",
					"description":_("Additional Need"),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Fees Type",
					"description":_("Fees Type"),
					"onboard": 1,
				},
			{
					"type": "doctype",
					"name": "Obligation",
					"description":_("Obligation"),
					"onboard": 1,
				},

{
					"type": "doctype",
					"name": "Territory",
					"description":_("Territory"),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Nationality",
					"description":_("Nationality"),
					"onboard": 1,
				},

			]
		},
		{
			"label": _("Beneficiary"),
			"items": [
				{
					"type": "doctype",
					"name": "The Base",
					"description":_("The Base"),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Beneficiary Request",
					"description":_("Beneficiary Request"),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Aid Renewal",
					"description":_("Aid Renewal"),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Beneficiary",
					"description":_("Beneficiary"),
					"onboard": 1,
				},
								
			]
		},
		{
			"label": _("Decision"),
			"items": [
			
				{
					"type": "doctype",
					"name": "Beneficiary Aids Entry",
					"description":_("Beneficiary Aids Entry"),
					"onboard": 1,
				},
			{
					"type": "doctype",
					"name": "Beneficiary Aids Payment",
					"description":_("Beneficiary Aids Payment"),
					"onboard": 1,
				},
								
			]
		},
		
	]