# Copyright (c) 2022, Sowaan and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import requests
import time
from frappe.utils import get_request_site_address
from frappe.model.document import Document


class Pike13Settings(Document):
    pass


@frappe.whitelist()
def get_auth_code_url():
    doc = frappe.get_doc('Pike13 Settings')
    redirect_uri = (
        "https://pike13.com/oauth/authorize?client_id="
        + doc.client_id+"&response_type=code&redirect_uri="
        + doc.redirect_uri
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
def sync_invoices():
    doc = frappe.get_doc('Pike13 Settings')
    pike13_sites = frappe.get_all("Pike13 Site", filters={"enabled": 1})
    if (len(pike13_sites) == 0):
        frappe.throw(
            _("Pike13 sites not found. Please make atleast one pike13 site and try again")
        )

    for x in pike13_sites:
        site = frappe.get_doc("Pike13 Site", x)
        sync_invoice_for_single_site(site, doc)

    return "Success"


def sync_invoice_for_single_site(site, doc):
    if check_payment_modes(site, doc):
        get_invoices_from_pike13(site, doc)


def check_payment_modes(site, doc):
    headers = {
        "Authorization": "Bearer "+doc.access_token
    }
    try:
        r = requests.get(
            site.pike13_site_url+"/api/v2/desk/payments/configuration", headers=headers).json()
    except requests.exceptions.HTTPError:
        button_label = frappe.bold(_("Get Access Token"))
        frappe.throw(
            _(
                "Something went wrong during the people sync. Click on {0} to generate a new one."
            ).format(button_label)
        )
    payment_config = r.get("payment_configuration")
    accepted_types = payment_config.get("accepted_types")
    not_found_in_erp = []
    for x in accepted_types:
        found = False
        for y in site.pike13_to_erp_mode_of_payment_mapping:
            if y.pike13_mode_of_payment == x:
                found = True

        if (not found):
            not_found_in_erp.append(x)

    if (len(not_found_in_erp) > 0):
        site.status = "Please map these mode of payments in Site then sync invoices again: " + \
            (','.join(not_found_in_erp))
        site.save()
        frappe.msgprint(
            msg=_(
                "<b style='color:red'>"+site.pike13_site_url +
                "</b><br>Please map these mode of payments in Site then sync invoices again. <br><br>" +
                ('<br>'.join(not_found_in_erp))
            )
        )
        return False

    return True


def get_invoices_from_pike13(site, doc):
    headers = {
        "Authorization": "Bearer "+doc.access_token
    }

    sync_from = site.synced_till
    while (1 == 1):
        try:
            r = requests.get(site.pike13_site_url+"/api/v2/desk/invoices?per_page=100&state=closed&created_since=" +
                             str(sync_from), headers=headers).json()
        except requests.exceptions.HTTPError:
            button_label = frappe.bold(_("Get Access Token"))
            frappe.throw(
                _(
                    "Something went wrong during the people sync. Click on {0} to generate a new one."
                ).format(button_label)
            )
        invoices = r.get("invoices")
        print("invoicesinvoices", invoices)
        last_invoice = insert_invoices_from_pike13(invoices, doc, site)
        sync_from = last_invoice.get("invoice_date")

        if r.get("next") is None:
            break

    frappe.msgprint(
        msg=_(
            "<b style='color:green'>"+site.pike13_site_url +
            "</b>: Invoices synced successfully!"
        )
    )


def insert_invoices_from_pike13(invoices, doc, site):
    headers = {
        "Authorization": "Bearer "+doc.access_token
    }
    curr_invoice = {}
    for x in invoices:
        erp_invoices = frappe.get_all("Sales Invoice", filters={
            "pike13_record_id": x.get("id")
        })
        # if length is more than 0 then this invoice is already synced with erp
        if (len(erp_invoices) == 0):
            try:
                r = requests.get(site.pike13_site_url+"/api/v2/desk/invoices/" +
                                 str(x.get("id")), headers=headers).json()
            except requests.exceptions.HTTPError:
                button_label = frappe.bold(_("Get Access Token"))
                frappe.throw(
                    _(
                        "Something went wrong during the people sync. Click on {0} to generate a new one."
                    ).format(button_label)
                )
            curr_invoice = r.get("invoices")[0]

            erp_customer = site.default_customer
            erp_items = None

            # check customer from erp
            if (curr_invoice.get("person") is not None):
                customer = curr_invoice.get("person")
                erp_customer = get_erp_customer(customer.get("id"), doc, site)

            # check items from erp
            if (curr_invoice.get("invoice_items") is not None):
                items = curr_invoice.get("invoice_items")
                erp_items = get_erp_items(items, doc, site)

            sales_tax_template = site.sales_tax_template
            # if tax template is not defined in the pike13 settings then use default one
            if sales_tax_template is None:
                default_tax_templates = frappe.get_all("Sales Taxes and Charges Template",
                                                       filters={
                                                           "is_default": 1
                                                       }
                                                       )
                if (len(default_tax_templates) > 0):
                    sales_tax_template = default_tax_templates[0].name

            si = frappe.new_doc("Sales Invoice")
            si.customer = erp_customer
            si.set_posting_time = 1
            si.posting_date = curr_invoice.get("invoice_date")
            si.due_date = curr_invoice.get("invoice_date")
            si.pike13_record_id = curr_invoice.get("id")
            si.pike13_invoice_number = curr_invoice.get("invoice_number")
            si.taxes_and_charges = sales_tax_template
            si.debit_to = site.receivable_account
            si.update_stock = 1
            si.set_warehouse = site.warehouse

            # link cost center to invoice if provided in pike13 site configuration
            if site.cost_center is not None:
                si.cost_center = site.cost_center

            for i in curr_invoice.get("payments"):
                si.is_pos = 1
                method_name = i.get("description")
                for j in site.pike13_to_erp_mode_of_payment_mapping:
                    if method_name == j.pike13_mode_of_payment:
                        print("*********payment amount************")
                        print(i.get("amount"))
                        si.append("payments", {
                            "mode_of_payment": j.erp_mode_of_payment,
                            "amount": i.get("amount_cents")/100
                        })
                        break

            for i in curr_invoice.get("invoice_items"):
                db_items = frappe.get_all("Item", filters={
                    "name": i.get("name").strip()
                })
                if (len(db_items) > 0):
                    erp_item = db_items[0]
                    discount = 0
                    rate = i.get("amount_cents")
                    if i.get("discount_total_cents") is not None:
                        rate = rate + i.get("discount_total_cents")
                    # for dis in i.get("adjustments"):
                    # 	if dis.get("type") == "Discount":
                    # 		discount += dis.get("amount_cents")

                    # print('******DISCOUNT*******')
                    # print(str(round(discount/100,2)))
                    si.append("items", {
                        "item_code": erp_item.name,
                        "rate": round(rate/100, 2),
                        "qty": 1
                    })

            si.set_missing_values()

            print(str(x.get("id"))+":" +
                  curr_invoice.get("invoice_date")+":"+str(erp_customer))

            si.insert(ignore_permissions=True)

            # this below code is to submit the invoice,
            # we will do once the integration would be stable

            # si.docstatus = 1
            # si.posting_date = curr_invoice.get("invoice_date")
            # si.save()

    if curr_invoice:
        site.synced_till = curr_invoice.get("invoice_date")
        site.save()
        frappe.db.commit()
    return curr_invoice


def get_erp_customer(id, doc, site):
    erp_customer = frappe.get_all("Customer", filters={
        "pike13_customer_id": id
    })
    if (len(erp_customer) == 0):
        # customer is not present in erp, insert it
        headers = {
            "Authorization": "Bearer "+doc.access_token
        }
        try:
            r = requests.get(
                site.pike13_site_url+"/api/v2/desk/people/"+str(id), headers=headers).json()
        except requests.exceptions.HTTPError:
            frappe.throw(
                _(
                    "Something went wrong during the customer sync from pike13."
                )
            )

        people = r.get("people")[0]
        customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "pike13_customer_id": people.get("id"),
                "customer_name": people.get("name"),
                "customer_group": "All Customer Groups",
                "territory": "All Territories",
                "email_id": people.get("email"),
                "mobile_no": people.get("phone"),
                # "address_line1": people.get("address")
            }
        ).insert(ignore_permissions=True)

        frappe.db.commit()
        return customer.name

    return erp_customer[0].name


def get_erp_items(items, doc, site):
    erp_items = []
    for x in items:
        item_detail = x.get("detail")
        items_in_db = frappe.get_all("Item",
                                     filters={
                                         "pike13_item_code": item_detail.get("product_id")
                                     },
                                     fields=['name', 'pike13_item_code']
                                     )
        if (len(items_in_db) == 0):
            # item is not present in erp by pike13 code, lets try with item name
            item = None
            if (not frappe.db.exists("Item", {"name": x.get("name")})):
                item = frappe.get_doc(
                    {
                        "doctype": "Item",
                        "item_code": x.get("name"),
                        "pike13_item_code": item_detail.get("product_id"),
                        "item_name": x.get("name"),
                        "item_group": "All Item Groups",
                        "stock_uom": "Nos",
                        "is_stock_item": 1 if x.get("detail").get("type") == "Retail" else 0,
                        "standard_rate": x.get("amount")
                    }
                ).insert(ignore_permissions=True)
            else:
                item = frappe.get_doc("Item", x.get("name"))
                item.pike13_item_code = item_detail.get("product_id")
                item.save()

            erp_items.append({
                "name": item.name,
                "pike13_item_code": item.pike13_item_code
            })
        else:
            erp_items.append({
                "name": items_in_db[0].get("name"),
                "pike13_item_code": items_in_db[0].get("pike13_item_code")
            })

    frappe.db.commit()
    return erp_items
