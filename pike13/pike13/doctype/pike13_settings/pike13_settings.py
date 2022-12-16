# Copyright (c) 2022, Sowaan and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe.utils import get_request_site_address
from frappe.model.document import Document


class Pike13Settings(Document):
	pass

@frappe.whitelist()
def get_auth_code_url():
	doc = frappe.get_doc('Pike13 Settings')
	redirect_uri = (
		"https://pike13.com/oauth/authorize?client_id="
		+doc.client_id+"&response_type=code&redirect_uri="
		+doc.redirect_uri
	)

	return {
		"url": redirect_uri
	}

@frappe.whitelist()
def get_access_token():
	doc = frappe.get_doc('Pike13 Settings')
	data = {
		"client_id": doc.client_id,
		"client_secret": doc.client_secret,
		"grant_type": doc.grant_type,
		"code": doc.auth_code,
		"redirect_uri": doc.redirect_uri,
	}

	try:
		r = requests.post("https://pike13.com/oauth/token", data=data).json()
	except requests.exceptions.HTTPError:
		button_label = frappe.bold(_("Get Access Token"))
		frappe.throw(
			_(
				"Something went wrong during the token generation. Click on {0} to generate a new one."
			).format(button_label)
		)

	return r.get("access_token")

@frappe.whitelist()
def sync_people():
	doc = frappe.get_doc('Pike13 Settings')
	headers = {
		"Authorization": "Bearer "+doc.access_token
	}

	try:
		r = requests.get(doc.pike13_site_url+"/api/v2/desk/people", headers=headers).json()
	except requests.exceptions.HTTPError:
		button_label = frappe.bold(_("Get Access Token"))
		frappe.throw(
			_(
				"Something went wrong during the token generation. Click on {0} to generate a new one."
			).format(button_label)
		)
	print("#########SUCCESS###########")
	people = r.get("people")
	print(r.get("total_count"))
	print(len(people))
	for x in people:
		print(x.get("first_name"))
	return "Success"#r.get("access_token")


