import urllib.parse
import hashlib
import hmac
import base64
import time


class Credentials:
    def __init__(self):
        self.API_key = "keykey"
        self.private_key = "secretsecret"

    def transform_private_key(self, data, urlpath):
        """ Sign request data according to Kraken's scheme.

                :param data: API request parameters
                :type data: dict
                :param urlpath: API URL path sans host
                :type urlpath: str
                :returns: signature digest
                """
        postdata = urllib.parse.urlencode(data)

        # Unicode-objects must be encoded before hashing
        encoded = (str(data['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()

        signature = hmac.new(base64.b64decode(self.private_key),
                             message, hashlib.sha512)
        sigdigest = base64.b64encode(signature.digest())

        return sigdigest.decode()


    def get_header(self, data, urlpath):
        headers = {
            'API-Key': self.API_key,
            'API-Sign': self.transform_private_key(data, urlpath)
        }

        return headers


def main():
    cred = Credentials()
    apiversion = '0'
    method = 'Balance'
    data = {}
    data['nonce'] = int(1000*time.time())
    urlpath = '/' + apiversion + '/private/' + method

    headers = {
        'API-Key': cred.API_key,
        'API-Sign': cred.transform_private_key(data, urlpath)
    }
    print(headers)


if __name__ == '__main__':
    main()