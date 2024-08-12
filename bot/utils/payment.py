import os

from dotenv import load_dotenv
from yoomoney import Client, Quickpay
from uuid import uuid4

load_dotenv(".env")

PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN") 
CLIENT_PAYMENT_TOKEN = os.getenv("CLIENT_PAYMENT_TOKEN")

client = Client(CLIENT_PAYMENT_TOKEN)

def create_payment(amount):
    label = str(uuid4())
    quickpay = Quickpay(
        receiver=PAYMENT_TOKEN,
        quickpay_form="button",
        targets="Покупка VPN",
        paymentType="AC",
        sum=amount,
        label=label,
        successURL="https://t.me/blazervpnbot"
    )
    return quickpay.redirected_url, label

def check(payment_id):
    history = client.operation_history(label=payment_id).operations
    print(history)
    if history != None:
        for operation in history:
            if operation.status == 'success':
                return True
            else:
                return False
    else:
        return False
 