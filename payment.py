import yookassa 
from yookassa import Payment
import uuid
from tokens import Account_payment_id, Secret_payment_key

yookassa.Configuration.account_id = Account_payment_id
yookassa.Configuration.secret_key = Secret_payment_key

def create_payment(amount, chat_id):
    id_key = str(uuid.uuid4())
    payment = Payment.create({
            "amount": {
                "value": amount,
                "currency": "RUB" 
            },
        'payment_method_data': { 
            'type': 'bank_card'
        },
        'confirmation': {
            'type': 'redirect',
            'return_url': 'https://t.me/blazervpnbot'
        },
        'capture': True,
        'metadata': {
            'chat_id': chat_id
        },
        'description': 'Описание товара...'
    }, id_key)

    return payment.confirmation.confirmation_url, payment.id

def check(payment_id):
    payment = yookassa.Payment.find_one(payment_id)
    if payment.status == 'succeeded':
        return payment.metadata
    else:
        return False