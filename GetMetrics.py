import requests
import json
import time, datetime
import os.path

import crypto_list
import const


class GetAllMetrics:
    def __init__(self):
        # URL Maker
        self.uri = "https://api.kraken.com"
        self.version = "0"
        self.public = "public"
        self.ticker = "Ticker?pair="
        self.time = "Time"
        self.url_maker = "{}/{}/{}/{}"

        # Time Information
        self.starttime = time.time()
        self.interval_time = 60.0

        # Currencies
        self.currencies = crypto_list.__cur__

        # CSV File
        self.filename_maker = "{}_{}"
        self.path_csv = "crypto_infos/{}.csv"
        self.header = "Date,High,Low,OpenPrice,Close,Average\n"
        self.data_maker = "{0},{1:.2f},{2:.2f},{3:.2f},{4:.2f},{5:.2f}\n"

    def get_server_time_from_kraken_api(self):
        url = self.url_maker.format(self.uri, self.version, self.public, self.time)
        response = requests.get(url)
        if response.status_code == 200:
            js = json.loads(response.content.decode(const.__encodage__))
            unixtime = js['result']['unixtime']
            rfc1123 = js['result']['rfc1123']
            return unixtime, rfc1123
        else:
            return '0', '0'

    def get_all_information_from_kraken_api(self, currency):
        url = self.url_maker.format(self.uri, self.version, self.public, self.ticker) + currency
        response = requests.get(url)
        if response.status_code == 200:
            js = json.loads(response.content.decode(const.__encodage__))
            return js['result'][currency]

    def insert_header(self, currency):
        file = open(self.path_csv.format(currency), "w")
        file.write(self.header)
        file.close()

    def format_information(self, currency, server_timestamp):

        req = self.get_all_information_from_kraken_api(currency)
        high = float(req['h'][1])
        low = float(req['l'][1])
        open_market = float(req['o'])
        close_market = float(req['c'][0])

        moy = (float(high) + float(low) + float(open_market)) / 3
        current_time = datetime.datetime.fromtimestamp(server_timestamp)

        csv_data = self.data_maker.format(current_time, high, low, open_market, close_market, moy)

        return csv_data

    def write_to_csv(self, filename, data):
        if not os.path.isfile(self.path_csv.format(filename)):
            self.insert_header(filename)
        file = open(self.path_csv.format(filename), "a")
        file.write(data)
        file.close()

    def start_collecting_information(self):
        starttime = time.time()
        while True:
            for cur in self.currencies:
                unxitime, rfc1123 = self.get_server_time_from_kraken_api()
                filename = self.filename_maker.format(cur, self.currencies[cur][1])
                data = self.format_information(self.currencies[cur][1], unxitime)
                self.write_to_csv(filename, data)
            time.sleep(self.interval_time - ((time.time() - starttime) % self.interval_time))


def main():
    metrics = GetAllMetrics()
    metrics.start_collecting_information()


if __name__ == '__main__':
    main()
