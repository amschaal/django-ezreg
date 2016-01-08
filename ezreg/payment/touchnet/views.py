from rest_framework.decorators import api_view, permission_classes
from ezreg.models import Payment, Registration
from django.http.response import JsonResponse
from datetime import datetime
from ezreg.payment.touchnet.permissions import IPAddressPermission
import logging
from ezreg.payment.touchnet.processor import TouchnetPaymentProcessor


"""
EXT_TRANS_ID    The departmental identifier passed in to the UPay site. (100)
UPAY_SITE_ID    (See above) (3)
POSTING_KEY    (See above) (variable)
PMT_STATUS    "success" upon a successful payment, "cancelled" if the user clicks the cancel button on the form. (20)
Variables sent only upon a successful payment:
PMT_AMT    The amount of the payment charged to the card. (numeric)
PMT_DATE    (today) (mm/dd/yyyy)
CARD_TYPE    The type of credit card used - spelled out (20)
TPG_TRANS_ID    The unique transaction ID assigned to the transaction by the payment gateway. (16)
NAME_ON_ACCT    Name of the card holder as shown on the card. (20)
ACCT_ADDR    Billing Address Street Address (40)
ACCT_CITY    Billing Address City Name (20)
ACCT_STATE    Billing Address State Code (2)
ACCT_ZIP    Billing Address Postal Code (20)


class Payment(models.Model):
    STATUS_UNPAID = 'UNPAID'
    STATUS_PENDING = 'PENDING'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_INVALID_AMOUNT = 'INVALID_AMOUNT'
    STATUS_PAID = 'PAID'
    STATUS_CHOICES = ((STATUS_UNPAID,'Unpaid'),(STATUS_PENDING,'Pending'),(STATUS_PAID,'Paid'),(STATUS_CANCELLED,'Cancelled'),(STATUS_INVALID_AMOUNT,'Invalid Amount'))
    processor = models.ForeignKey('PaymentProcessor',null=True,blank=True)
    status = models.CharField(max_length=10,default=STATUS_UNPAID,choices=STATUS_CHOICES)
    paid_at = models.DateTimeField(blank=True,null=True)
    registration = models.OneToOneField(Registration,related_name='payment')
    amount = models.DecimalField(decimal_places=2,max_digits=7)
    external_id = models.CharField(max_length=50,null=True,blank=True)
    data = JSONField(null=True,blank=True)
"""


@api_view(['POST'])
#@permission_classes([IPAddressPermission])
def postback(request):
    req = {k.upper():v for k,v in request.POST.items()} #Touchnet seems inconsistent about case
    logger = logging.getLogger('touchnet')
    try:
        print req.get('EXT_TRANS_ID')
        fid, registration_id = req.get('EXT_TRANS_ID').split(";")
        print registration_id
        registration = Registration.objects.get(id=registration_id)
        payment = registration.payment
        posting_key = TouchnetPaymentProcessor.get_posting_key(payment)
#         if  payment.processor.config.has_key('posting_key'):
        if posting_key != req.get('POSTING_KEY'):
#	    values = ', '.join([key+':'+value for key, value in req.items()])
            raise Exception("Invalid POSTING_KEY")
        if req.get('PMT_STATUS')=='success':
            payment.external_id = req.get('TPG_TRANS_ID')
            if float(req.get('PMT_AMT')) == float(payment.amount):
                payment.status = Payment.STATUS_PAID
                payment.paid_at = datetime.now()
                payment.save()
            else:
                payment.status = Payment.STATUS_INVALID_AMOUNT
                payment.save()
                raise Exception('Invalid amount posted %s, expecting %f' % (req.get('PMT_AMT'),payment.amount))
            payment.save()
        elif req.get('PMT_STATUS')=='cancelled':
            payment.status = Payment.STATUS_CANCELLED
            payment.save()
        return JsonResponse({'status':'ok','payment_status':payment.status})
    except Exception, e:
        # Get an instance of a logger
        logger.info("Error for EXT_TRANS_ID: %s"%req.get('EXT_TRANS_ID',''))
        logger.error(e.message)
        return JsonResponse({'status':'error'},status=400)
        
