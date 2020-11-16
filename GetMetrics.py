import requests
import json
import time, datetime

class GetAllMetrics:

    def get_all_informations(self, currency):
        response = requests.get("https://api.kraken.com/0/public/Ticker?pair=" + currency)
        data = []
        if response.status_code == 200:
            js = json.loads(response.content.decode('utf-8'))
            return js['result'][currency]

    def format_information(self, currency):
        file = open(currency + ".csv", "a")
        req = self.get_all_informations(currency)
        high = float(req['h'][1])
        low = float(req['l'][1])
        market = float(req['o'])
        moy = (float(high) + float(low) + float(market)) / 3
        current_time = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
        file.write("{0},{1:.2f},{2:.2f},{3:.2f},{4:.2f}\n".format(current_time,high,low, market, moy))
        file.close()

def main():
    currency = ['XETHZEUR', 'XXBTZEUR']
    metrics = GetAllMetrics()
    starttime = time.time()
    while True:
        for cur in currency:
            metrics.format_information(cur)
        time.sleep(60.0 - ((time.time() - starttime) % 60.0))

if __name__ == '__main__':
    main()