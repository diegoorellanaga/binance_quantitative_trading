import numpy as np
from binance.client import Client
from influxdb import InfluxDBClient
import zulu
from binance.websockets import BinanceSocketManager


class BinanceInfluxdb():
    
    def __init__(self,symbol = "IOTAUSDT",is_new_db = False,database ='binance_test_5',measurement= 'minute_tick',host='localhost', port=8086,api_key = "api_key",api_secret = "private_api_key" ):    
    
        self.database = database
        self.client = Client(api_key, api_secret)
        self.InfluxClient = InfluxDBClient(host='localhost', port=8086)
        
        if is_new_db:
            self.InfluxClient.create_database(self.database) 
        
        self.InfluxClient.switch_database(self.database)  
        self.InfluxClient.create_retention_policy(name='coin_policy',duration='INF',database=self.database,replication=1, default=True, shard_duration='4w')
        self.symbol = symbol
        self.measurement_name = measurement
        self.need_data_actualization = True
        
    def online_process_message(self,msg):
        
        measurement = self.measurement_name
        msg_type = "raw"
        self.insert_data_point_influxdb(msg,measurement,msg_type)
        
        if self.need_data_actualization:
            print("##############################one time update #####################################")
            current_time_num=msg["k"]["t"]/1000.0
            self.get_previous_point(current_time_num)
            self.need_data_actualization = False               
            
    def get_previous_point(self,current_time_num):

        count = 1    
      #  current_time_num=previous_msg["k"]["t"]/1000.0
        pre_previous_time = zulu.parse(current_time_num-60).isoformat() #I rest 60 seconds
        
        pre_previous_time_query=self.InfluxClient.query("select * from {2} WHERE time = '{0}' AND pair = '{1}';".format(pre_previous_time,self.symbol,self.measurement_name))
        
        while not len(list(pre_previous_time_query)):
            count = count+1
            pre_previous_time_loopty_loop = zulu.parse(current_time_num-count*60).isoformat()
            pre_previous_time_query=self.InfluxClient.query("select * from {2} WHERE time = '{0}' AND pair = '{1}';".format(pre_previous_time_loopty_loop,self.symbol,self.measurement_name))
            print("testing_time: {0}, count:".format(pre_previous_time_loopty_loop),count)

    
    
        event_type = 'kline'
        interval ='1m'     
        units = 'minute'
        num_of_units = count+2 #Just in case I added 2 units more
        msg_type = 'raw'
        #insert this amount of data to make sure I have the RAW DB updated
        self.insert_offline_tick_data(event_type,interval,units,num_of_units,msg_type)
    
    def insert_data_point_influxdb(self,msg,measurement,msg_type):

        if msg_type == 'raw':
            json_body4 = [
            {
                    "measurement": measurement,
                    "tags": {
                        "event_type": msg["e"],
                        "base_currency": msg["s"][:int(len(msg["s"])/2)],
                        "quote_currency": msg["s"][int(len(msg["s"])/2):],
                        "pair": msg["s"],
                        "interval": msg["k"]["i"]
                    },
                    "time": zulu.parse(msg["k"]["t"]/1000.0).isoformat(),#datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),#+'Z',
                    "fields": {
                        "open": float(msg["k"]["o"]),
                        "close":float(msg["k"]["c"]),
                        "high":float(msg["k"]["h"]),
                        "low":float(msg["k"]["l"]),
                        "high-low":float(msg["k"]["h"])-float(msg["k"]["l"]),
                        "close-open":float(msg["k"]["c"])-float(msg["k"]["o"]),
                        "volume":float(msg["k"]["v"]), #Base asset volume
                        "number_of_trades":int(msg["k"]["n"]),
                        "quote_volume":float(msg["k"]["q"]), #Quote asset volume
                        "active_buy_volume":float(msg["k"]["V"]), #Taker buy base asset volume
                        "active_buy_quote_volume":float(msg["k"]["Q"]), #Taker buy quote asset volume
                        "gain":-1000,
                        "lose":-1000,
                        "avg_gain":-1000,
                        "avg_lose":-1000,
                        "RSI":-1000,
                        "MACD":-1000,
                        "KDJ":-1000,
                        "DMI":-1000,
                        "OBV":-1000,
                        "MTM":-1000,
                        "EMA":-1000,
                        "VWAP":-1000,
                        "AVL":-1000,
                        "TRIX":-1000,
                        "StochRSI":-1000,
                        "EMV":-1000,
                        "WR":-1000,
                        "BOLL":-1000,
                        "SAR":-1000,
                        "CCI":-1000,
                        "MA":-1000,
                        "VOL":-1000
                    
                    
                    }
                }
            ]    
        self.InfluxClient.write_points(points=json_body4,retention_policy='coin_policy')
        print("inserting message with time: {0}, message type: {1}, measurement: {2}".format(json_body4[0]["time"],msg_type,measurement))

    def create_msg_from_history(self,event_type,interval,symbol,units,num_of_units,from_now=True,from_date=0,to_date=0): #update this to accept more ranges
        
        if from_now:
        #http://dateparser.readthedocs.io/en/latest/
            if units == 'hour':        
                raw_data=self.client.get_historical_klines(symbol, interval, "{0} hour ago UTC".format(num_of_units))
            elif units == 'day':
                raw_data=self.client.get_historical_klines(symbol, interval, "{0} day ago UTC".format(num_of_units))        
            elif units == 'week':
                raw_data=self.client.get_historical_klines(symbol, interval, "{0} week ago UTC".format(num_of_units))     
            elif units == 'month':
                raw_data=self.client.get_historical_klines(symbol, interval, "{0} month ago UTC".format(num_of_units))
            elif units == 'minute':
                raw_data=self.client.get_historical_klines(symbol, interval, "{0} minute ago UTC".format(num_of_units))         
    
        else:
            raw_data=self.client.get_historical_klines(symbol, interval,from_date,to_date)
            #klines = client.get_historical_klines("ETHBTC", Client.KLINE_INTERVAL_30MINUTE, "1 Dec, 2017", "1 Jan, 2018")
   
        list_of_msgs = list(np.zeros(len(raw_data),dtype=object))


        for i, raw_msg in enumerate(raw_data):
       
            if i%10000 == 0:
                print(i)
           
            list_of_msgs[i] =  {
                    "measurement": self.measurement_name,
                    "tags": {
                        "event_type": event_type,
                        "base_currency": symbol[:int(len(symbol)/2)],
                        "quote_currency": symbol[int(len(symbol)/2):],
                        "pair": symbol ,
                        "interval": interval
                    },
                    "time": zulu.parse(raw_msg[0]/1000.0).isoformat(),#datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),#+'Z',
                    "fields": {
                        "open": float(raw_msg[1]),
                        "close":float(raw_msg[4]),
                        "high":float(raw_msg[2]),
                        "low":float(raw_msg[3] ),
                        "high-low":float(raw_msg[2])-float(raw_msg[2]),
                        "close-open":float(raw_msg[4])-float(raw_msg[1]),
                        "volume":float(raw_msg[5]), #Base asset volume
                        "number_of_trades":int(raw_msg[8] ),
                        "quote_volume":float(raw_msg[7] ), #Quote asset volume
                        "active_buy_volume":float(raw_msg[9] ), #Taker buy base asset volume
                        "active_buy_quote_volume":float(raw_msg[10]), #Taker buy quote asset volume
                        "gain":-1000,
                        "lose":-1000,
                        "avg_gain":-1000,
                        "avg_lose":-1000,
                        "RSI":-1000,                   
                        "MACD":-1000,
                        "KDJ":-1000,
                        "DMI":-1000,
                        "OBV":-1000,
                        "MTM":-1000,
                        "EMA":-1000,
                        "VWAP":-1000,
                        "AVL":-1000,
                        "TRIX":-1000,
                        "StochRSI":-1000,
                        "EMV":-1000,
                        "WR":-1000,
                        "BOLL":-1000,
                        "SAR":-1000,
                        "CCI":-1000,
                        "MA":-1000,
                        "VOL":-1000                    
                    
                    }
                }
        return list_of_msgs      

    def insert_offline_data(self,list_of_msgs,measurement,msg_type):   
        
        self.InfluxClient.write_points(points=list_of_msgs,retention_policy='coin_policy')
        
    def insert_offline_tick_data(self,event_type,interval,units,num_of_units,msg_type,from_now=True,from_date=0,to_date=0):
        '''
        event_type = 'kline'
        interval ='1m'     
        symbol = "IOTAUSDT"
        units = 'hour'
        num_of_units = 24
        measurement_off ="offline_minute_tick"
        msg_type = 'raw'
        from_now = False
        from_date = "26Jun, 2018"     
        to_date = "27 Jun, 2018"  
        '''
        measurement =self.measurement_name
        symbol = self.symbol
        # forced symbol to be self.symbol because it has to be coherent to the websocket type of messages, this is not pretty but it works.
        list_of_msgs = self.create_msg_from_history(event_type,interval,symbol,units,num_of_units,from_now,from_date,to_date)
        self.insert_offline_data(list_of_msgs,measurement,msg_type)  
        return list_of_msgs      

    def websocket_start(self):
        
        self.bm =BinanceSocketManager(self.client)
        self.bm.start_kline_socket( self.symbol, self.online_process_message)
        self.bm.start()
        
    def websocket_close(self):        
        self.bm.close()


        
symbol_1 = "IOTAUSDT"
symbol_2=  "XRPUSDT"        
symbol_3 = "BTCUSDT"

f = open("/home/diego/Desktop/crypto/rl-crypto/Information/api_keys","r")
keys = f.readlines()
api_key = keys[0][:-1]
api_secret = keys[1][:-1]


##        
my_binance_influxdb_1 = BinanceInfluxdb(symbol=symbol_1,is_new_db=False,database='binance',api_key=api_key,api_secret=api_secret)
##my_binance_influxdb_1.insert_offline_tick_data(event_type = 'kline',interval ='1m',units = 'month',num_of_units = 6,msg_type = 'raw') 
###           
my_binance_influxdb_2 = BinanceInfluxdb(symbol=symbol_2,is_new_db=False,database='binance',api_key=api_key,api_secret=api_secret)
##my_binance_influxdb_2.insert_offline_tick_data(event_type = 'kline',interval ='1m',units = 'month',num_of_units = 6,msg_type = 'raw') 
#
##event_type,interval,units,num_of_units,msg_type
#
#
my_binance_influxdb_2.websocket_start()  
my_binance_influxdb_1.websocket_start() 





#my_binance_influxdb_1 = BinanceInfluxdb(symbol=symbol_3,is_new_db=False,database='binance',api_key=api_key,api_secret=api_secret)
#my_binance_influxdb_1.insert_offline_tick_data(event_type = 'kline',interval ='1m',units = 'month',num_of_units = 6,msg_type = 'raw') 
#my_binance_influxdb_1.websocket_start() 


    
