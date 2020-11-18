import requests
import json
import time, datetime
import os.path

import crypto_list
import const

from tradingBot import MoneyBot

class GetAllMetrics:
    def __init__(self):
        # URL Maker
        self.uri = "https://api.kraken.com"
        self.version = "0"
        self.public = "public"
        self.ticker = "Ticker?pair="
        self.asset_pairs = "AssetPairs"
        self.time = "Time"
        self.url_maker = "{}/{}/{}/{}"

        # Time Information
        self.starttime = time.time()
        self.interval_time = 30.0

        # Currencies
        self.currencies = crypto_list.__cur__

        # CSV File
        self.filename_maker = "{}_{}"
        self.path_csv = "crypto_infos/{}.csv"
        self.header = "Date,High,Low,OpenPrice,Close,Average,LowAverage,HighAverage,LargeAverage\n"
        self.data_maker = "{0},{1:.2f},{2:.2f},{3:.2f},{4:.2f},{5:.2f},{6:.2f},{7:.2f},{8:.2f}\n"
        self.new_header = False

        # Asset Pair File
        self.asset_filename = "assetlist.csv"
        self.asset_header_list = ['altname', 'wsname', 'base', 'quote']
        self.data_maker_asset = "{},{},{},{}\n"

        # Ticker information
        self.ask = 'a'
        self.bid = 'b'
        self.close = 'c'
        self.volume = 'v'
        self.volume_weighted_average_price = 'p'
        self.number_of_trades = 't'
        self.low_price = 'l'
        self.high_price = 'h'
        self.open_price = 'o'

        # Average
        self.average_last_values = 20

        self.order = 0
        self.achat = 0
        self.achat1 = 0
        self.limite = 0

    def get_server_time_from_kraken_api(self):
        url = self.url_maker.format(self.uri, self.version, self.public, self.time)
        response = requests.get(url)
        if response.status_code == 200:
            js = json.loads(response.content.decode(const.__encodage__))
            unixtime = js['result']['unixtime']
            rfc1123 = js['result']['rfc1123']
            return unixtime, rfc1123
        else:
            print(response)
            print(response.content.decode(const.__encodage__))
            print(json.loads(response.content.decode(const.__encodage__)))
            return '0', '0'

    def get_ticker_information_from_kraken_api(self, currency):
        url = self.url_maker.format(self.uri, self.version, self.public, self.ticker) + currency
        response = requests.get(url)
        if response.status_code == 200:
            js = json.loads(response.content.decode(const.__encodage__))
            return js['result'][currency]
        else:
            return []

    def get_assets_pairs_from_kraken_api(self):
        url = self.url_maker.format(self.uri, self.version, self.public, self.asset_pairs)
        response = requests.get(url)
        if response.status_code == 200:
            js = json.loads(response.content.decode(const.__encodage__))
            return js['result']

    def create_asset_pair_file(self, js):
        # if not os.path.isfile(self.asset_filename):
        self.insert_asset_pair_headers()
        file = open(self.asset_filename, 'a')
        for asset in js:
            tmp = []
            for li in self.asset_header_list:
                if '.d' in asset:
                    if "wsname" in li:
                        tmp.append("")
                    else:
                        tmp.append(js[asset][li])
                else:
                    tmp.append(js[asset][li])
            file.write(self.data_maker_asset.format(tmp[0], tmp[1], tmp[2], tmp[3]))

    def insert_header(self, currency):
        file = open(self.path_csv.format(currency), "w")
        file.write(self.header)
        file.close()

    def update_header(self, currency):
        file = open(self.path_csv.format(currency), "r")
        file.readline()
        tab = []
        for i in file.readlines():
            tab.append(i)
        file.close()
        file = open(self.path_csv.format(currency), "w")
        file.write(self.header)
        for i in tab:
            file.write(i)
        file.close()

    def insert_asset_pair_headers(self):
        file = open(self.asset_filename, "w")
        header = ""
        for i in self.asset_header_list:
            header = header + i + ','
        header = header[:-1] + '\n'
        file.write(header)
        file.close()

    def format_information(self, currency, server_timestamp, filename):
        req = self.get_ticker_information_from_kraken_api(currency)
        high = float(req['h'][1])
        low = float(req['l'][1])
        open_market = float(req['o'])
        close_market = float(req['c'][0])
        low_average, high_average, large_average = self.get_low_and_high_average(filename)

        moy = (float(high) + float(low) + float(close_market)) / 3
        current_time = datetime.datetime.fromtimestamp(server_timestamp)

        csv_data = self.data_maker.format(current_time, high, low, open_market, close_market, moy, low_average,
                                          high_average, large_average)

        return csv_data

    def write_to_csv(self, filename, data):
        if not os.path.isfile(self.path_csv.format(filename)):
            self.insert_header(filename)
        if self.new_header:
            self.update_header(filename)
        file = open(self.path_csv.format(filename), "a")
        file.write(data)
        file.close()

    def start_collecting_information(self):
        starttime = time.time()
        while True:
            for cur in self.currencies:
                unxitime, rfc1123 = self.get_server_time_from_kraken_api()
                filename = self.filename_maker.format(cur, self.currencies[cur][1])
                data = self.format_information(self.currencies[cur][1], unxitime, filename)
                self.write_to_csv(filename, data)
            time.sleep(self.interval_time - ((time.time() - starttime) % self.interval_time))
            self.check_actual_trend()

    def get_low_and_high_average(self, currency):
        if not os.path.isfile(self.path_csv.format(currency)):
            return 0.0, 0.0
        tab = []
        low_average = 0
        high_average = 0
        large_average = 0
        file = open(self.path_csv.format(currency), "r")
        file_lines = file.readlines()
        file.close()
        lines = len(file_lines)
        if lines > self.average_last_values + 1:
            for i in range(lines - self.average_last_values, lines):
                tab.append(file_lines[i].replace('\n', '').split(','))

            for i in tab:
                low_average = low_average + float(i[2])
                high_average = high_average + float(i[1])
                large_average = large_average + float(i[2]) + float(i[1]) + float(i[4])
            low_average = low_average / self.average_last_values
            high_average = high_average / self.average_last_values
            large_average = large_average / (self.average_last_values * 3)
        else:
            test = 0
            for i in range(1, lines):
                tab.append(file_lines[i].replace('\n', '').split(','))
                test = test + 1
            for i in tab:
                low_average = low_average + float(i[2])
                high_average = high_average + float(i[1])
                large_average = large_average + float(i[2]) + float(i[1]) + float(i[4])
            low_average = low_average / (lines - 1)
            high_average = high_average / (lines - 1)
            large_average = large_average / ((lines - 1) * 3)
        return low_average, high_average, large_average

    def get_number_of_line(self, currency):
        if not os.path.isfile(self.path_csv.format(currency)):
            return 0

        file = open(self.path_csv.format(currency), "r")
        file_lines = file.readlines()
        file.close()
        return len(file_lines)

    def read_last_line(self, currency):
        if not os.path.isfile(self.path_csv.format(currency)):
            print("Crypto not found")
            return None
        else:
            file = open(self.path_csv.format(currency), "r")
            file_lines = file.readlines()
            file.close()
            return file_lines[len(file_lines)-1]

    def check_actual_trend(self, crypto="Compound_COMPEUR"):
        ret = self.read_last_line(crypto)
        time_average = float(ret.split(',')[5])
        large_average = float(ret.split(',')[8])
        bot = MoneyBot()
        euro = float(bot.define_eur_volume())
        comp = float(bot.define_crypto_volume("COMP"))
        self.order, js = bot.get_open_order()

        euro = euro / 3 # on trade avec 1 tiers de ce qu'on a
        print("ORDER : " + str(self.order))
        if self.order == 0:
            print("Cond 1 - order = 0")
            if time_average > large_average:
                print("Cond 2 TimeA > Largea : {} > {}".format(time_average,large_average))
                if euro > 4 :
                    self.achat = float(ret.split(',')[4])
                    self.achat1 = self.achat + ((1 / 100) * self.achat)
                    self.limite = self.achat - ((1 / 100) * self.achat)
                    print("achat : {}, achat+1% : {}, limit: {}".format(self.achat, self.achat1, self.limite))
                    bot.create_order_buy(self.achat, (euro/self.achat), "COMP")
                """elif time_average < large_average:
                    self.achat = float(ret.split(',')[4])
                    print("vente : {}".format(self.achat))"""
            else:
                print("Cond 3 TimeA Not > Largea : {} > {}".format(time_average,large_average))
        elif time_average < large_average:
            if comp > 0:
                bot.create_order_sell(comp, "COMP")
        elif self.order > 0:
            if float(ret.split(',')[4]) >= self.achat1:
                print("MAX LIMITE : {}".format(self.achat1))
            elif float(ret.split(',')[4]) <= self.limite:
                print("Perte : {}".format(self.limite))

def main():
    metrics = GetAllMetrics()
    js = metrics.get_assets_pairs_from_kraken_api()
    metrics.create_asset_pair_file(js)
    metrics.start_collecting_information()


if __name__ == '__main__':
    main()
