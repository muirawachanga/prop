/**
 * Created by alex on 9/3/16.
 */

frappe.listview_settings['Billing Period'] = {
    add_fields: ['period_name', 'start_date', 'end_date', 'period_type'],
    onload: function(listview) {
        var method = 'property.property_management.doctype.billing_period.billing_period.create_monthly_periods'
        console.log(listview);
        listview.page.add_action_item(__("Create Monthly Periods"), function() {
            frappe.call({
                method: method,
                callback: function(data, res){
                    listview.refresh();
                    frappe.msgprint(__('Monthly Periods for current year created successfully.'));
                }
            });
        });
    }
}