import requests
import json
import time
import credentials

class MoneyBot:
    def __init__(self):
        self.win_percent = 1.5
        self.loss_percent = 2.0
        self.uri = "https://api.kraken.com"
        self.api_version = '0'
        self.private = "private"
        self.crypto_actif = []

    def private_query(self, method, data={}):
        cred = credentials.Credentials()
        data['nonce'] = int(1000*time.time())

        urlpath = "/{}/{}/{}".format(self.api_version,self.private, method)
        complete_url = self.uri+urlpath
        headers = cred.get_header(data,urlpath)
        response = requests.post(complete_url, data=data, headers=headers)
        if response.status_code == 200:
            js = json.loads(response.content.decode('utf-8'))
            return js
        else:
            return None

    def get_personal_balance(self):
        method = "Balance"
        js = self.private_query(method)
        if len(js['error']) > 0:
            print("problème de Requete : Balance")
        else:
            if len(js['result']) > 0:
                balance = {}
                self.crypto_actif.append(js['result'])
                for i in js['result']:
                    # print("{} : {}".format(i, js['result'][i]))
                    balance[i] = js['result'][i]
                return balance

    def get_open_order(self):
        method = "OpenOrders"
        order_number = 0
        js = self.private_query(method)
        if len(js['error']) > 0:
            print("problème de Requete : " + method)
        else:
            order_number = len(js['result']['open'])

        return order_number, js['result']['open']

    def check_actual_trend(self, ligne, crypto="Ethereum_XETHZEUR"):
        print(ligne)
        time_average = ligne.split(',')[5]
        large_average = ligne.split(',')[8]

    def create_order_buy(self, actual_price, volume=0, crypto="XETHZEUR"):
        method = "AddOrder"

        actual_price_plus1 = actual_price + ((1/100) * actual_price)
        actual_price_moins1 = actual_price - ((1 / 100) * actual_price)
        data = {"pair": crypto,
                "type": "buy",
                "ordertype": "market",
                "volume": "{}".format(volume),
                "close[ordertype]": "stop-loss-limit",
                "close[price]": "{}".format(actual_price_moins1),
                "close[price2]": "{}".format(actual_price_plus1)
                }

        print(data)
        # js = self.private_query(method, data)
        # print(js)

    def define_crypto_volume(self, crypto="XETHZEUR"):
        balance = self.get_personal_balance()
        monnaie = crypto.replace("ZEUR", "").replace("EUR","")
        if monnaie in balance:
            volume = balance[monnaie]

        return volume

    def define_eur_volume(self):
        balance = self.get_personal_balance()

        return balance['ZEUR']

    def create_order_sell(self, volume, crypto="XETHZEUR"):
        method = "AddOrder"

        data = {"pair": crypto,
                "type": "sell",
                "ordertype": "market",
                "volume": "{}".format(volume),
                }

        print(data)
        # self.private_query(method,data)


def main():
    bot = MoneyBot()
    bot.get_personal_balance()
    volume = bot.define_crypto_volume("COMPEUR")
    volume_ZEUR = bot.define_eur_volume()
    print(bot.get_open_order())



if __name__ == '__main__':
    main()
