// Copyright (c) 2022, Sowaan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pike13 Site', {
	// refresh: function(frm) {

	// }
	get_pike13_mode_of_payments: function(frm) {
		if(frm.doc.pike13_site_url == undefined)
			frappe.throw("Please provide Site Url in the field")
		frappe.call({
			method: "pike13.pike13.doctype.pike13_site.pike13_site.get_pike13_mode_of_payments",
			args: {
				"pike13_site_url": frm.doc.pike13_site_url
			},
			callback: function(r) {
				if (!r.exc) {
					r.message.forEach(element => {
						var isExistes = false;
						frm.doc.pike13_to_erp_mode_of_payment_mapping.forEach(e => {
							if (e.pike13_mode_of_payment === element){
								isExistes = true;
								return false;
							}
						})
						if(!isExistes){
							var childTable = frm.add_child("pike13_to_erp_mode_of_payment_mapping");
							childTable.pike13_mode_of_payment=element
						}
					});
					frm.refresh_fields("pike13_to_erp_mode_of_payment_mapping");
					// frm.set_value('access_token', r.message)
					// frm.save();
				}
			},
			freeze: true,	
			freeze_message: __('Getting mode of payments from pike13...')
		});
	}
});
