// Copyright (c) 2016, Bituls Company Limited and contributors
// For license information, please see license.txt

//cur_frm.add_fetch("owner_contract", "property_name", "property_name" );

frappe.ui.form.on('Landlord Remittance', {
  setup: function(frm) {

  },

  onload: function(frm) {
    if(!frm.doc.period_start || !frm.doc.period_end){
      var today = new Date();
      var start_date = new Date(today.getFullYear(), today.getMonth(), 1);
      var end_date = new Date(today.getFullYear(), today.getMonth() + 1, 0);
      //Set only if not set
      if(!frm.doc.period_start){
        frm.set_value('period_start', start_date);
      }
      if(!frm.doc.period_end){
        frm.set_value('period_end', end_date);
      }
    }
  },

  refresh: function(frm) {
    //frm.disable_save();
  },

	owner_contract: function(frm) {
    frm.fields_dict.load_remittance_data.$input.addClass("btn-primary");
	},

  include_unpaid_invoices: function(frm) {
    frm.fields_dict.load_remittance_data.$input.addClass("btn-primary");
	},

  load_remittance_data: function(frm) {
    return frappe.call({
      method: "get_details",
      doc: frm.doc,
      callback: function(r, rt) {
        frm.fields_dict.load_remittance_data.$input.removeClass("btn-primary");
        frm.refresh()
      }
    });
  },
});

cur_frm.cscript.lookup_obj = function lookup(array, prop, value) {
    for (var i = 0, len = array.length; i < len; i++)
        if (array[i] && array[i][prop] === value) return array[i];
}

cur_frm.cscript.recalculate_collections = function(frm){
  var ci = frm.doc.collection_invoices;
  var cd = frm.doc.collections_details; //Invoice item
  //console.log(frm);
  //Remove all the items whose invoice has been removed.
  frm.fields_dict["collections_details"].df.read_only = 0;
  frm.refresh_field("collections_details");
  $.each(cd, function(i, obj){
    var inv = cur_frm.cscript.lookup_obj(ci, 'invoice', obj.invoice);
    if(!inv){
      frm.fields_dict["collections_details"].grid.grid_rows_by_docname[obj.name].remove();
    }
  });
  frm.fields_dict["collections_details"].df.read_only = 1;
  frm.refresh_field("collections_details");
  // Total Collection and Remittable collections
  var tc = flt(0);
  var rc = flt(0);
  $.each(ci, function(i, obj){
    tc = flt(tc + flt(obj.grand_total));
    rc = flt(rc + flt(obj.remittance_amount));
  });
  frm.doc.remittable_collections = rc;
  frm.doc.total_collections = tc;
  cur_frm.cscript.lookup_obj(frm.doc.remittance_summary, "description", "Total Collections").amount = tc;
  cur_frm.cscript.lookup_obj(frm.doc.remittance_summary, "description", "Remittable Collections").amount = rc;


  // Commission exempt and commission eligible collections_details
  var cex = flt(0);
  var cel = flt(0);
  var base_amt = flt(0);

  $.each(frm.doc.collections_details, function(i, obj){
    if (!obj.is_remittable) return;
    if (obj.remit_full_amount) return;
    base_amt = flt(base_amt + flt(obj.item_total));
  });
  cel = base_amt;
  cex = flt(rc - base_amt);
  cur_frm.cscript.lookup_obj(frm.doc.remittance_summary, "description", "Commission Exempted Collections").amount = cex;
  cur_frm.cscript.lookup_obj(frm.doc.remittance_summary, "description", "Commission Eligible Collections").amount = cel;

  // Calculate commission and remmitance
  var cr = flt(frm.doc.commission_rate/100);
  var ca = flt(base_amt * cr);
  frm.doc.management_fee = ca;
  var net_rem = flt(rc - flt(ca + frm.doc.deductible_expenses));
  frm.doc.remittance_amount = net_rem;
  cur_frm.cscript.lookup_obj(frm.doc.remittance_summary, "description", "Commission Charged").amount = ca;
  cur_frm.cscript.lookup_obj(frm.doc.remittance_summary, "description", "Net Amount To Landlord").amount = net_rem;

  frm.refresh_fields();

}

frappe.ui.form.on('Landlord Expense Invoices', 'expense_invoices_remove', function(frm){

});

frappe.ui.form.on('Landlord Collection Invoices', 'collection_invoices_remove', function(frm){
  console.log(frm);
  //console.log(frm.doc.commission_rate);
  cur_frm.cscript.recalculate_collections(frm);
});
