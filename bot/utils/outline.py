import os

from outline_vpn.outline_vpn import OutlineVPN
from dotenv import load_dotenv

load_dotenv('.env')


OUTLINE_FINLAND_API = os.getenv("OUTLINE_FINLAND_API")
OUTLINE_FINLAND_CERF = os.getenv("OUTLINE_FINLAND_CERF")

client = OutlineVPN(OUTLINE_FINLAND_API, OUTLINE_FINLAND_CERF)

def gb_to_bytes(gb: float):
    """Функция для исчисления количества байт из гигабайт

    Args:
        gb (float): количество гигабайт

    Returns:
        [int]: байты, переведенные из гигабайт
    """
    bytes_in_gb = 1000 ** 3
    return int(gb * bytes_in_gb)

def create_new_key(key_id: str = None, name: str = None, data_limit_gb: float = None):
    client.create_key(key_id=key_id, name=name, data_limit=gb_to_bytes(data_limit_gb))

def find_keys_info(key_id: str):
    vpn_keys = client.get_key(key_id)
    return vpn_keys.access_url + f"#BLAZER VPN #{key_id}"

def delete_key(key_id: str):
    client.delete_key(key_id)