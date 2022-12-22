// Copyright (c) 2022, Sowaan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pike13 Settings', {
	onload: function(frm) {
		const params = new URLSearchParams(location.search);//console.log(frm)
		if(params.get('code'))
			frm.set_value('auth_code', params.get('code'))
			frm.save();
	},
	get_auth_code: function(frm) {
		frappe.call({
			method: "pike13.pike13.doctype.pike13_settings.pike13_settings.get_auth_code_url",
			// args: {
			// 	"reauthorize": reauthorize
			// },
			callback: function(r) {
				if (!r.exc) {
					frm.save();
					window.open(r.message.url);
				}
			}
		});
	},
	get_access_token: function(frm) {
		frappe.call({
			method: "pike13.pike13.doctype.pike13_settings.pike13_settings.get_access_token",
			callback: function(r) {
				if (!r.exc) {
					frm.set_value('access_token', r.message)
					frm.save();
				}
			}
		});
	},
	sync_invoices: function(frm) {
		frappe.call({
			method: "pike13.pike13.doctype.pike13_settings.pike13_settings.sync_invoices",
			callback: function(r) {
				if (!r.exc) {
					// frm.set_value('access_token', r.message)
					// frm.save();
				}
			},
			freeze: true,	
			freeze_message: __('Syncing data from pike13...')
		});
	}
});

