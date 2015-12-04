from rest_framework.decorators import api_view
from ezreg.models import Payment

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
    STATUS_PAID = 'PAID'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_CHOICES = ((STATUS_UNPAID,'Unpaid'),(STATUS_PENDING,'Pending'),(STATUS_PAID,'Paid'))
    processor = models.ForeignKey('PaymentProcessor',null=True,blank=True)
    status = models.CharField(max_length=10,default=STATUS_UNPAID,choices=STATUS_CHOICES)
    paid_at = models.DateTimeField(blank=True,null=True)
    registration = models.OneToOneField(Registration,related_name='payment')
    amount = models.DecimalField(decimal_places=2,max_digits=7)
    data = JSONField(null=True,blank=True)
"""


@api_view(['POST'])
def postback(request):
    fid, payment_id = request.data['EXT_TRANS_ID']
    payment = Payment.objects.get(id=payment_id)
    #check payment.processor.config['posting_key'] == request.data['POSTING_KEY']
    if request.data['PMT_STATUS']=='success':
        pass
    elif request.data['PMT_STATUS']=='cancelled':
        pass
        