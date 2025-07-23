# import sys
# sys.path.append("D:/code/python/projects/trading/serious_bot")

import pkg_resources
import subprocess
import sys
import datetime as dt
import time 
import re
from pprint import pprint
import warnings
import asyncio
import tables as tb

modules = ["pandas", "pybit", "IPython"]

for m in modules:
    try:
        pkg_resources.get_distribution(m)
    except pkg_resources.DistributionNotFound:
        subprocess.run([sys.executable, '-m', 'pip', 'install', m])

from pybit.unified_trading import HTTP 
from pybit.unified_trading import WebSocket
from pybit import exceptions
import pandas as pd
from IPython.display import display

# from func import indicators as inds



warnings.filterwarnings('ignore')


now_dt = dt.datetime.now()
now_timestamp = int(time.mktime(now_dt.timetuple())) * 1000
SYMBOL = "SHIB1000USDT"
INTERVAL = 5
SIDE = "Buy"
QTY = "500"
# SYMBOL = "BTCUSDT"


class API():
    intervals = ["1", "5", "15", "60","120", "240", "D", "W", "M"]

    def __init__(self, key, demo=True, websocket=True):
        keys = []
        api_key= "no"
        secret_key = "no"
        try:
            f = open(f"D:/code/python/projects/trading/ginger_bot/api_secret.txt", "r+", encoding="utf-8")
            keys =[x.strip("\n, =-") for x in f.read().split("\n") if x.strip("\n, =-")]
            f.close()
        except:
            print("\ntxt file not found")

        for i in range(len(keys)):
            if keys[i] == key:
                api_key = keys[i+2]
                secret_key = keys[i+4]
                break
            
        print(api_key, secret_key)

        self.client = HTTP(
            api_key=api_key,
            api_secret=secret_key,
            testnet=False,
            max_retries=10,
            retry_delay=3,
            demo=demo,
        # recv_window=60000
        )
        if websocket:
            self.ws = WebSocket(
                testnet=False,
                channel_type="linear",
                retries=200,
                restart_on_error=True,
            )
            for symb in self.get_symbol_list():
                for inter in API.intervals:
                    self.ws.kline_stream(
                        interval=inter,
                        symbol=symb,
                        callback=self.handle_message,
                        )  



    def get_info(self, symbol, interval, limit, start=None, end=None):

        candles = self.client.get_kline(category="linear", 
                            symbol=symbol, 
                            interval=interval,
                            start=start,
                            end=end,
                            limit=limit)["result"]["list"]
        
        try:
            self.params.get("test")
        except:
            self.params = {}

        if self.params.get("last_closed", False):
            df = pd.DataFrame(candles[1:])    
        else:
            df = pd.DataFrame(candles)
        if self.params.get("volume", False):
            df = df.iloc[:,:7]
            df = df.drop(5, axis=1)
            df.columns=["time", "open", "high", "low", "close", "volume"]
        else:
            df = df.iloc[:,:5]
            df.columns=["time", "open", "high", "low", "close"]

        df = df.astype(float)
        df["time"] = pd.to_datetime(df["time"], unit="ms")
        if self.params.get("moscow", True):
            df["time"] = df["time"]+ dt.timedelta(hours=3)
        if  self.params.get("time_to_ind", True):
            df = tb.time_to_index(df)
        if self.params.get("set_pf", False):
            df = tb.set_postfix(df, self.params.get("interval"), self.params.get("pf", None))
        df = tb.set_direction(df, self.params.get("direction", "decreace"))
        return df
    


    def get_data(self, symbols, intervals, limit=200, last_closed=False, volume=False, moscow=True, time_to_ind=True, direction="decrease", 
                 pf=None, set_pf=False, start=None, end=None):
        if type(symbols) == str:
            self.symbols = [symbols]
        else:
            self.symbols = symbols
        if type(intervals) == int or type(intervals) == str:
            self.intervals = [str(intervals)]
        else:
            self.intervals = [str(x) for x in intervals]
        self.data = {}
        self.params = dict(last_closed=last_closed,
                           volume=volume,
                           moscow=moscow,
                           time_to_ind=time_to_ind, 
                           direction=direction,
                           pf=pf, 
                           set_pf=set_pf)
        for symb in self.symbols:
            symb_dict = {}
            for inter in self.intervals:
                while True:
                    try:
                        data = self.get_info(symb, inter, limit, start, end)
                        symb_dict[inter] = dict(data=data)
                    except:
                        time.sleep(1)
                    else:
                        break
            self.data[symb] = symb_dict


    async def a_get_info(self, symbol, interval, limit, start=None, end=None):
         return self.get_info(symbol, interval, limit, start=start, end=end)
    
    
    async def a_get_data(self, symbols, intervals, limit=200, last_closed=False, volume=False, moscow=True, time_to_ind=True, direction="decrease", 
                          pf=None, set_pf=False, start=None, end=None):
        if type(symbols) == str:
            self.symbols = [symbols]
        else:
            self.symbols = symbols
        if type(intervals) == int or type(intervals) == str:
            self.intervals = [str(intervals)]
        else:
            self.intervals = [str(x) for x in intervals]
        tasks = []
        self.data = {}
        self.params = dict(last_closed=last_closed,
                           volume=volume,
                           moscow=moscow,
                           time_to_ind=time_to_ind, 
                           direction=direction,
                           pf=pf, 
                           set_pf=set_pf)
        for symb in self.symbols:
            self.data[symb] = {}
            for inter in self.intervals:
                self.data[symb][inter] = {}
                # print(symb, inter)
                while True:
                    try:
                        task = asyncio.create_task(self.a_get_info(symb, inter, limit, start, end))
                        # self.data[symb][inter] = {"data": task}
                        tasks.append([symb, inter , task])
                        
                        
                    except:
                        time.sleep(1)
                    else:
                        break
        for task in tasks:
            self.data[task[0]][task[1]]["data"] = await task[2]
            print()
            print(task[0])
            print(task[1])
            print(self.data[task[0]][task[1]]["data"].head())
            print(self.data[task[0]][task[1]]["data"].tail())
                
      
    def update_data(self, limit=2, collect=False, control=False):

        if self.data:
            for symb in self.symbols:
                for inter in self.intervals:
                    while True:
                        try:
                            last_data = self.get_info(symb, inter, limit=limit)
                            # data = self.data[symb][inter]["data"]
                            # data_length = len(self.data[symb][inter]["data"])
                        except:
                            time.sleep(1)
                        else:
                            break
                    if control:
                        display(
                            f"\n=========================== DATA {symb} {inter} ===========================\n", self.data[symb][inter]["data"].head(), "\n", self.data[symb][inter]["data"].tail(), 
                            "\n======================================================================\n","\n#####################\n##### length of data:\n#####", 
                            len(self.data[symb][inter]["data"]), "\n#####################\n",f"\n========================= LAST DATA {symb} {inter} ========================\n", 
                            last_data, "\n======================================================================\n"
                            )

                    if last_data.head(1).index != self.data[symb][inter]["data"].head(1).index:
                        # self.data[symb][inter]["data"] = pd.concat([last_data.head(1), self.data[symb][inter]["data"]])
                        
                        self.data[symb][inter]["data"].loc[last_data.index[0]] = last_data.values[0]
                        self.data[symb][inter]["data"].sort_index(inplace=True, ascending=False)
                        if not collect:
                            self.data[symb][inter]["data"] = self.data[symb][inter]["data"].head(len(self.data[symb][inter]["data"])-1)

                        if control:
                            display(
                                "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", 
                                f"\n======================= UPDATED DATA {symb} {inter} =======================\n", self.data[symb][inter]["data"].head(), "\n", self.data[symb][inter]["data"].tail(), 
                                "\n======================================================================\n","\n######################\n##### length of data:\n#####", 
                                len(self.data[symb][inter]["data"]), "\n######################\n","\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                                )
                        # return True
                    else:
                        if not self.params.get("last_closed"):
                            self.data[symb][inter]["data"].iloc[:1] = last_data.head(1)
                            self.data[symb][inter]["data"].iloc[1:2] = last_data.tail(1)
                            if control:
                                print("######################\n###### replaced ######\n######################")


    def handle_message(self, message, collect=False):
        # self.message = message
        symb = re.findall(r'\w+USDT$', message["topic"])[0]
        inter = message["data"][0]["interval"]
        try:
            if symb in self.symbols and inter in self.intervals:
                print()
                print()
                print(symb)
                
                print(inter)
                data_list = [message["data"][0]["start"],
                            message["data"][0]["open"],
                            message["data"][0]["high"],
                            message["data"][0]["low"],
                            message["data"][0]["close"]]
                if self.params.get("volume", False):
                    data_list.append(message["data"][0]["turnover"])
                    columns=["time", "open", "high", "low", "close", "volume"]
                else:
                    columns=["time", "open", "high", "low", "close"]   
                df = pd.DataFrame([data_list])
                df.columns=columns
                df = df.astype(float)
                df["time"] = pd.to_datetime(df["time"], unit="ms")
                df["time"] = df["time"]+ dt.timedelta(hours=3)
                last_data = tb.time_to_index(df)
                print(last_data)
                print()
                if last_data.index != self.data[symb][inter]["data"].head(1).index:
                    self.data[symb][inter]["data"] = pd.concat([last_data, self.data[symb][inter]["data"]])
                    if not collect:
                        self.data[symb][inter]["data"] = self.data[symb][inter]["data"].head(len(self.data[symb][inter]["data"])-1)
                else:
                    if not self.params.get("last_closed"):
                        self.data[symb][inter]["data"].loc[last_data.index[0]] = last_data.values[0]
                        self.data[symb][inter]["data"].sort_index(inplace=True, ascending=False)
                print(self.data[symb][inter]["data"].head())
                print(self.data[symb][inter]["data"].tail())
        except:
            pass
            # time.sleep(5)

    
    
    def create_order(self, symbol, side, qty, price, stop_loss, take_profit):
        try: 
            result = self.client.place_order(
                category="linear", 
                symbol=symbol,
                side=side,
                qty=qty,
                orderType="limit",
                price=price, 
                stopLoss=stop_loss,
                takeProfit=take_profit,
        #         timeInForce="GTC",
        #         marketUnit = "quoteCoin"
            )

        except exceptions.InvalidRequestError as e:
            print("Bybit Request Error", e.status_code, e.message, sep=" | ")
        except exceptions.FailedRequestError as e:
            print("Request Failed", e.status_code, e.message, sep=" | ")
        except Exception as e:
            print(e)
        else:
            return result
        
    def check_symb(self, symbol):
        try:
            self.client.get_kline(category="linear",
                              symbol=symbol,
                              interval=1,
                              limit=1)
            return True
        except:
            return False
        
    def get_symbol_list(self):
        while True:
            try:
                r = self.client.get_instruments_info(category="linear", limit=1000)["result"]["list"]
                # l = [x["symbol"] for x in r]
                l = [x["symbol"] for x in r if re.findall(r'\w+USDT$', x["symbol"])]
                # l = l = [x["symbol"] for x in r if x["symbol"][0] == "A"]
                return l
            except:
                time.sleep(1)



