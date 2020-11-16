import requests
import json
import time, datetime
import os.path
import crypto_list

class GetAllMetrics:

    def get_all_informations(self, currency):
        response = requests.get("https://api.kraken.com/0/public/Ticker?pair=" + currency)
        data = []
        if response.status_code == 200:
            js = json.loads(response.content.decode('utf-8'))
            return js['result'][currency]

    def insert_header(self, currency):
        file = open("crypto_infos/" + currency + ".csv", "w")
        file.write("Date,High,Low,OpenPrice,Close,Average\n")
        file.close()

    def format_information(self, currency):

        req = self.get_all_informations(currency)
        high = float(req['h'][1])
        low = float(req['l'][1])
        open_market = float(req['o'])
        close_market = float(req['c'][0])

        moy = (float(high) + float(low) + float(open_market)) / 3
        current_time = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

        str = "{0},{1:.2f},{2:.2f},{3:.2f},{4:.2f},{5:.2f}\n".format(current_time,high,low, open_market, close_market, moy)


        return str

    def write_to_csv(self, filename, data):
        if not os.path.isfile("crypto_infos/" + filename + ".csv"):
            self.insert_header(filename)
        file = open("crypto_infos/" + filename + ".csv", "a")
        file.write(data)
        file.close()

def main():
    currency = crypto_list.__cur__
    metrics = GetAllMetrics()
    starttime = time.time()
    while True:
        for cur in currency:
            filename = "{}_{}".format(cur, currency[cur][1])
            data = metrics.format_information(currency[cur][1])
            metrics.write_to_csv(filename, data)
        time.sleep(60.0 - ((time.time() - starttime) % 60.0))

if __name__ == '__main__':
    main()