import requests
import os

from dotenv import load_dotenv
from uuid import uuid4

load_dotenv(".env")

NICEPAY_MERCHANT_ID = os.getenv("NICEPAY_MERCHANT_ID") 
NICEPAY_SECRET = os.getenv("NICEPAY_SECRET_KEY")

def create_nicepay_payment(amount: int, email: str):
    order_id = uuid4()
    data = {'merchant_id': NICEPAY_MERCHANT_ID,
            "secret": NICEPAY_SECRET, 
            "order_id": f'{order_id}', 
            "customer": f'{email}', 
            "amount": f'{amount * 100}', 
            'currency': 'RUB', 
            "description": 'Покупка BLAZER VPN',
            "success_url": 'https://t.me/blazervpnbot',
            "fail_url": 'https://t.me/blazervpnbot'}
    
    response = requests.post('https://nicepay.io/public/api/payment', data=data)
    if response.status_code == 200 and response.json()['status'] == 'success':
        return response.json()['data']['link'], response.json()['data']['payment_id']
    else:
        print(response.json())
        return None
    
def nicepay_check(payment_id):
    response = requests.get(f"https://lk.blazer-host.ru/result/telegram")

    if response.status_code == 200:
        print("response code - 200")
        try:
            data = response.json()
            print(f"Response: {data}")
            if data['order_id'] == payment_id:
                if data['result'] == "success":
                    print("result == success")
                    return True
                else:
                    print("result != success")
                    return False
            else:
                print("order_id != payment_id")
                return False
        except Exception as e:
            print(f"Error decoding JSON: {e}")
            print(response.text)
            return False
    else:
        print(f"Error: {response.status_code} - {response.text}")   
        return False
