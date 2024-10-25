import os

from dotenv import load_dotenv
from yoomoney import Client, Quickpay
from uuid import uuid4

load_dotenv(".env")

PAYMENT_TOKEN = os.getenv("YOOMONEY_PAYMENT_TOKEN") 
CLIENT_PAYMENT_TOKEN = os.getenv("YOOMONEY_CLIENT_PAYMENT_TOKEN")

client = Client(CLIENT_PAYMENT_TOKEN)

def create_yoomoney_payment(amount):
    label = str(uuid4())
    quickpay = Quickpay(
        receiver=PAYMENT_TOKEN,
        quickpay_form="button",
        targets="Покупка личной сети",
        paymentType="AC",
        sum=amount,
        label=label,
        successURL="https://t.me/blazervpnbot"
    )
    print(label)
    return quickpay.redirected_url, label

def yoomoney_check(payment_id):
    history = client.operation_history(label=str(payment_id)).operations
    if history != []:
        for operation in history:
            if operation.status == 'success':
                return True
            else:
                return False
    else:
        return False
