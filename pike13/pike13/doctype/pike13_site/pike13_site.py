# Copyright (c) 2022, Sowaan and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import requests
from frappe.model.document import Document

class Pike13Site(Document):
	pass

@frappe.whitelist()
def get_pike13_mode_of_payments(pike13_site_url=None):
	doc = frappe.get_doc('Pike13 Settings')
	headers = {
		"Authorization": "Bearer "+doc.access_token
	}
	try:
		r = requests.get(pike13_site_url+"/api/v2/desk/payments/configuration", headers=headers).json()
	except requests.exceptions.HTTPError:
		frappe.throw(
			_(
				"Something went wrong while getting mode of payments from pike13."
			)
		)
	payment_config = r.get("payment_configuration")
	accepted_types = payment_config.get("accepted_types")
	return accepted_types
