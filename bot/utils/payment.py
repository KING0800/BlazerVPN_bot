import yookassa 
import uuid
import os 

from yookassa import Payment
from dotenv import load_dotenv

load_dotenv(".env")
ACCOUNT_PAYMENT_ID_TOKEN = os.getenv("ACCOUNT_PAYMENT_ID_TOKEN") 
SECRET_PAYMENT_KEY_TOKEN = os.getenv("SECRET_PAYMENT_KEY_TOKEN")

yookassa.Configuration.account_id = ACCOUNT_PAYMENT_ID_TOKEN
yookassa.Configuration.secret_key = SECRET_PAYMENT_KEY_TOKEN

def create_payment(amount, chat_id, payment_type, user_email):
    id_key = str(uuid.uuid4())
    payment = Payment.create({
    "amount": {
        "value": amount,
        "currency": "RUB" 
    },
    'payment_method_data': { 
        'type': f'{payment_type}'
    },
    'confirmation': {
        'type': 'redirect',
        'return_url': 'https://t.me/blazervpnbot'
    },
    'capture': True,
    'metadata': {
        'chat_id': chat_id
    },
    'description': 'Blazer VPN',
    'receipt': {
        'customer': {
            "email": user_email 
        },
        'items': [
            {
                "description": "BLAZER - HOSTING SERVICES",
                "quantity": "1",
                "amount": {
                    "value": amount,
                    "currency": 'RUB'
                },
                "vat_code": "1"
            }
        ]
    }
}, id_key)
    return payment.confirmation.confirmation_url, payment.id


def check(payment_id):
    payment = yookassa.Payment.find_one(payment_id)
    if payment.status == 'succeeded':
        return payment.metadata
    else:
        return False
