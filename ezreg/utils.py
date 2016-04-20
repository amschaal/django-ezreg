def format_registration_data(event,registrations,encode_utf8=True):
    form_fields = []
    if event.form_fields:
        form_fields = [field for field in event.form_fields if 'layout' not in field['type']]
    reg_data = {
                'fields':{'registered':{'label':'Registered','type':'datetime'},
                          'first_name':{'label':'First Name'},
                          'last_name':{'label':'Last Name'},
                          'email':{'label':'Email'},
                          'status':{'label':'Status'},
                          'payment.processor':{'label':'Processor'},
                          'payment.status':{'label':'Payment Status'},
                          'payment.paid_at':{'label':'Paid at'},
                          'payment.amount':{'label':'Amount'},
                          'payment.external_id':{'label':'External_id'},
                          },
                'data':[]
                }
    for field in form_fields:
        reg_data['fields'][field['name']]={'label':field['label'],'type':field['type']}
    
    for processor in event.payment_processors.all():
        exportable_fields = processor.get_processor().exportable_fields
        for name,label in exportable_fields.iteritems():
            reg_data['fields']['processor_%d_%s'%(processor.id,name)] = {'label':label}
    
    for r in registrations:
        data = {'registered':r.registered.strftime('%Y-%m-%d %H:%M'), 'first_name':r.first_name, 'last_name':r.last_name, 'email': r.email, 'status':r.status}

        #Add custom form field values
        for field in form_fields:
            data[field['name']] = r.get_form_value(field['name'])
        
        payment = r.get_payment()

        #Add selected payment fields
        if payment:
            data.update({'payment.processor':payment.processor,'payment.status':payment.status,'payment.paid_at':payment.paid_at,'payment.amount':payment.amount, 'payment.external_id':payment.external_id})
            #Add selected payment processor fields
            for processor in event.payment_processors.all():
                exportable_fields = processor.get_processor().exportable_fields
                for name,label in exportable_fields.iteritems():
                    if payment.data:
                        val = payment.data.get(name,None)
                        if val:
                            data['processor_%d_%s'%(processor.id,name)] = val
        if encode_utf8:
            for key, val in data.iteritems():
                data[key] = unicode(val).encode("utf-8") if val else None
        reg_data['data'].append(data)
    return reg_data