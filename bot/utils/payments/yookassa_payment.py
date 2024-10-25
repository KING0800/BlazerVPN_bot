from yookassa import Payment, Configuration
from uuid import uuid4
import os
from dotenv import load_dotenv

load_dotenv('.env')

YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY")
YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID")

Configuration.account_id = YOOKASSA_SHOP_ID
Configuration.secret_key = YOOKASSA_SECRET_KEY


def create_yookassa_payment(amount, chat_id):
    label = str(uuid4())
    payment = Payment.create({
        "amount": {
            "value": amount,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/blazervpnbot"
        },
        "capture": True,
        "description": "Оплата личной сети",
        "metadata": {
            "chat_id": chat_id
        },
        'description': 'Оплата личной сети'
        }, label)
    return payment.confirmation.confirmation_url, payment.id
    
def yookassa_check(label):
    payment = Payment.find_one(payment_id=label)
    if payment.status == "succeeded":
        return True
    else:
        return False