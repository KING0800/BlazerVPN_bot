from outline_vpn.outline_vpn import OutlineVPN

api_url = ""
cert_sha256 = ""

client = OutlineVPN(api_url, cert_sha256)

for keys in client.get_key():
    print(keys.access_key)
    