import base64
import json
import os

from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Util.number import bytes_to_long, long_to_bytes

license_data = {
    'version': 1,
    'licensee': {
        'Name': 'null',
        'Company': 'null',
        'Email': 'null@null.com'
    },
    'issued_at': '2023-01-01',
    'expires_at': '2100-12-31',
    'notify_admins_at': '2100-12-01',
    'notify_users_at': '2100-12-01',
    'block_changes_at': '2100-12-10',
    'cloud_licensing_enabled': False,
    'offline_cloud_licensing_enabled': False,
    'auto_renew_enabled': False,
    'seat_reconciliation_enabled': False,
    'operational_metrics_enabled': False,
    'generated_from_customers_dot': False,
    'restrictions': {
        'active_user_count': 99999
    }
}


class License:
    def __init__(self, rsa_key=None):
        self.rsa_key = rsa_key

    def generate_license(self, license_json):
        rsa_key = RSA.generate(2048) if self.rsa_key is None else self.rsa_key
        aes_key = os.urandom(16)
        aes_iv = os.urandom(16)
        license_plaintext = json.dumps(license_json).encode()
        if len(license_plaintext) % 16 > 0:
            pad = 16 - len(license_plaintext) % 16
            license_plaintext = license_plaintext + pad.to_bytes(1) * pad
        encrypt_data = AES.new(aes_key, AES.MODE_CBC, aes_iv).encrypt(license_plaintext)
        pad = rsa_key.size_in_bytes() - 19
        encrypt_key = pow(bytes_to_long(bytes.fromhex(f'0001{"ff" * pad}00{aes_key.hex()}')), rsa_key.d, rsa_key.n)
        encrypt_key = encrypt_key.to_bytes(1 + encrypt_key.bit_length() // 8)
        encrypt_license = {
            'data': base64.b64encode(encrypt_data).decode(),
            'key': base64.b64encode(encrypt_key).decode(),
            'iv': base64.b64encode(aes_iv).decode(),
        }
        encrypt_license = json.dumps(encrypt_license).encode()
        encrypt_license = base64.b64encode(encrypt_license)
        if self.rsa_key is None:
            with open('rsa.key', 'wb') as f:
                f.write(rsa_key.export_key())
            with open('.license_encryption_key.pub', 'wb') as f:
                f.write(rsa_key.public_key().export_key())
        with open('GitLabEE.gitlab-license', 'wb') as f:
            f.write(encrypt_license)
        return None

    def parse_license(self, encrypt_license):
        encrypt_license = base64.b64decode(encrypt_license)
        encrypt_license = json.loads(encrypt_license.decode())
        encrypt_data = base64.b64decode(encrypt_license['data'].replace('\n', ''))
        encrypt_key = base64.b64decode(encrypt_license['key'].replace('\n', ''))
        iv = base64.b64decode(encrypt_license['iv'])
        key = long_to_bytes(
            pow(bytes_to_long(encrypt_key), self.rsa_key.e, self.rsa_key.n),
            self.rsa_key.size_in_bytes()
        )[-16:]
        data = AES.new(key, AES.MODE_CBC, iv).decrypt(encrypt_data)
        if data[-1] != 125:
            # 不以}结尾
            data = data[:-data[-1]]
        print(json.dumps(json.loads(data.decode()), indent=2))


if __name__ == '__main__':
    # 生成
    # License().generate_license(license_data)
    License(rsa_key=RSA.import_key(open('rsa.key').read())).generate_license(license_data)
    # 解析
    obj = License(rsa_key=RSA.import_key(open('.license_encryption_key.pub').read()))
    with open('GitLabEE.gitlab-license') as f:
        obj.parse_license(f.read())
