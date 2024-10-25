import os

from outline_vpn.outline_vpn import OutlineVPN
from dotenv import load_dotenv

load_dotenv('.env')

OUTLINE_GERMANY_API = os.getenv("OUTLINE_GERMANY_API")
OUTLINE_GERMANY_CERF = os.getenv("OUTLINE_GERMANY_CERF")

OUTLINE_SWEDEN_API = os.getenv("OUTLINE_SWEDEN_API")
OUTLINE_SWEDEN_CERF = os.getenv("OUTLINE_SWEDEN_CERF")

OUTLINE_NETHERLANDS_API = os.getenv("OUTLINE_NETHERLANDS_API")
OUTLINE_NETHERLANDS_CERF = os.getenv("OUTLINE_NETHERLANDS_CERF")

germany_client = OutlineVPN(api_url=OUTLINE_GERMANY_API, cert_sha256=OUTLINE_GERMANY_CERF)
sweden_client = OutlineVPN(api_url=OUTLINE_SWEDEN_API, cert_sha256=OUTLINE_SWEDEN_CERF)
netherlands_client = OutlineVPN(api_url=OUTLINE_NETHERLANDS_API, cert_sha256=OUTLINE_NETHERLANDS_CERF)

def gb_to_bytes(gb: float):
    """Функция для исчисления количества байт из гигабайт

    Args:
        gb (float): количество гигабайт

    Returns:
        [int]: байты, переведенные из гигабайт
    """
    bytes_in_gb = 1000 ** 3
    return int(gb * bytes_in_gb)

def create_new_key(key_id: str = None, name: str = None, data_limit_gb: float = None, location: str = None):
    if "Германия" in location:
        client = germany_client
    elif "Швеция" in location:
        client = sweden_client
    elif "Нидерланды" in location:
        client = netherlands_client
    client.create_key(key_id=key_id, name=name, data_limit=gb_to_bytes(data_limit_gb))

def find_keys_info(key_id: str, location: str = None):
    if "Германия" in location:
        client = germany_client
    elif "Швеция" in location:
        client = sweden_client
    elif "Нидерланды" in location:
        client = netherlands_client
    vpn_keys = client.get_key(key_id)
    correct_location = location.split(" ")[0]
    return vpn_keys.access_url + f"#{correct_location} #{key_id}"

def delete_key(key_id: str, location: str = None):
    if "Германия" in location:
        client = germany_client
    elif "Швеция" in location:
        client = sweden_client
    elif "Нидерланды" in location:
        client = netherlands_client
    client.delete_key(key_id)