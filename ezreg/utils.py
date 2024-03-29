from ezreg.templatetags.ezreg_filters import form_value
def format_registration_data(event,registrations,encode_utf8=True):
    form_fields = []
    if event.form_fields:
        form_fields = [field for field in event.form_fields if 'layout' not in field['type']]
    reg_data = {
                'fields':{'registered':{'label':'Registered','type':'datetime'},
                          'id':{'label':'Registration ID'},
                          'first_name':{'label':'First Name'},
                          'last_name':{'label':'Last Name'},
                          'email':{'label':'Email'},
                          'department':{'label':'Department'},
                          'status':{'label':'Status'},
                          'admin_notes':{'label':'Admin Notes'},
                          'payment.price':{'label':'Price'},
                          'payment.processor':{'label':'Processor'},
                          'payment.status':{'label':'Payment Status'},
                          'payment.paid_at':{'label':'Paid at'},
                          'payment.amount':{'label':'Amount'},
                          'payment.coupon':{'label':'Coupon code'},
                          'payment.refunded':{'label':'Refunded'},
                          'payment.external_id':{'label':'External_id'},
                          'payment.admin_notes':{'label':'Payment admin notes'}
                          },
                'data':[]
                }
    for field in form_fields:
        reg_data['fields'][field['name']]={'label':field['label'],'type':field['type']}
    
    for processor in event.payment_processors.all():
        exportable_fields = processor.get_processor().exportable_fields
        for name,label in exportable_fields.items():
            reg_data['fields']['processor_%d_%s'%(processor.id,name)] = {'label':label}
    
    for r in registrations:
        data = {'registered':r.registered.strftime('%Y-%m-%d %H:%M'), 'id': r.id, 'first_name':r.first_name, 'last_name':r.last_name, 'email': r.email, 'department': r.department, 'status':r.status,'admin_notes':r.admin_notes}

        #Add custom form field values
        for field in form_fields:
            data[field['name']] = r.get_form_value(field['name'])
        
        payment = r.get_payment()

        #Add selected payment fields
        if payment:
            data.update({'payment.price':r.price.name,'payment.processor':payment.processor,'payment.status':payment.status,'payment.paid_at':payment.paid_at,'payment.amount':payment.amount,'payment.coupon':r.price.coupon_code,'payment.refunded':payment.refunded, 'payment.external_id':payment.external_id, 'payment.admin_notes':payment.admin_notes})
            #Add selected payment processor fields
            for processor in event.payment_processors.all():
                exportable_fields = processor.get_processor().exportable_fields
                for name,label in exportable_fields.items():
                    if payment.data:
                        val = payment.data.get(name,None)
                        if val:
                            data['processor_%d_%s'%(processor.id,name)] = val
        elif r.price:
            data.update({'payment.price':r.price.name})
            if True:#r.price.amount == 0:
                data.update({'payment.amount':r.price.amount})
        if encode_utf8:
            for key, val in data.items():
                data[key] = str(form_value(val)) if val is not None else None
        reg_data['data'].append(data)
    return reg_data