#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 13:43:59 2018

@author: root
"""


from binance.client import Client
import datetime
from influxdb import InfluxDBClient
import zulu
import copy
from binance.websockets import BinanceSocketManager
######Binance############

api_key = "api_key" #DELETE THIS!!!
api_secret = "private_api_key" #DELETE THIS!!!


#client = Client(api_key, api_secret)

############################
######InfluxDB##############

#InfluxClient = InfluxDBClient(host='localhost', port=8086)

#InfluxClient.create_database('binance_test_5')  #I need to create the db in the first run. 
#InfluxClient.switch_database('binance_test_5')    
#InfluxClient.create_retention_policy(name='coin_policy',duration='INF',database='binance_test_5',replication=1, default=True, shard_duration='4w')
############################

#I will give the influxdb client as a parameter as long with the  binance client.
class binanceInfluxdb():
    def __init__(self,symbol = "IOTAUSDT",is_new_db = False,database ='binance_test_5',measurement= 'minute_tick',host='localhost', port=8086,api_key = "api_key",api_secret = "private_api_key" ):    
    
        self.database = database
        self.client = Client(api_key, api_secret)
        self.InfluxClient = InfluxDBClient(host='localhost', port=8086)
        
        if is_new_db:
            self.InfluxClient.create_database(self.database) 
        
        self.InfluxClient.switch_database(self.database)  
        self.InfluxClient.create_retention_policy(name='coin_policy',duration='INF',database=self.database,replication=1, default=True, shard_duration='4w')
        self.previous_msg = ""
        self.previous_start_time = "hello"
        self.symbol = symbol
        self.measurement_name = measurement
        self.need_data_actualization = True
        
    def online_process_message(self,msg):
        
        measurement = self.measurement_name
        msg_type = "raw"
        self.insertMinuteTickValueIntoInfluxDB(msg,measurement,msg_type)
        
        if self.need_data_actualization:
            print("##############################one time update #####################################")
            current_time_num=msg["k"]["t"]/1000.0
            self.get_previous_point(current_time_num)
            self.need_data_actualization = False               
            
    def get_previous_point(self,current_time_num):
#this method assumes that RSI and RAW are equally updated
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
    
    def insertMinuteTickValueIntoInfluxDB(self,msg,measurement,msg_type):
        
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
                        "gain":-1,
                        "lose":-1,
                        "avg_gain":-1,
                        "avg_lose":-1,
                        "RSI":-1                   
                    
                    
                    }
                }
            ]    
        elif msg_type == 'RSI':
            json_body4 = [
            {
                    "measurement": measurement,
                    "tags": {
                        "event_type": msg["event_type"],
                        "base_currency": msg["base_currency"],
                        "quote_currency": msg["quote_currency"],
                        "pair": msg["pair"],
                        "interval": msg["interval"]
                        },
                    "time": msg["time"],#datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),#+'Z',
                    "fields": {
                        "open": float(msg["open"]),
                        "close":float(msg["close"]),
                        "high":float(msg["high"]),
                        "low":float(msg["low"]),
                        "high-low":float(msg["high-low"]),
                        "close-open":float(msg["close-open"]),
                        "volume":float(msg["volume"]), #Base asset volume
                        "number_of_trades":float(msg["number_of_trades"]),
                        "quote_volume":float(msg["quote_volume"]), #Quote asset volume
                        "active_buy_volume":float(msg["active_buy_volume"]), #Taker buy base asset volume
                        "active_buy_quote_volume":float(msg["active_buy_quote_volume"]), #Taker buy quote asset volume
                        "gain":float(msg["gain"]),
                        "lose":float(msg["lose"]),
                        "avg_gain":float(msg["avg_gain"]),
                        "avg_lose":float(msg["avg_lose"]),
                        "RSI":float(msg["RSI"])
                    }
                }
            ]    
        elif msg_type == 'stochRSI':
            json_body4 = [
            {
                    "measurement": measurement,
                    "tags": {
                        "event_type": msg["event_type"],
                        "base_currency": msg["base_currency"],
                        "quote_currency": msg["quote_currency"],
                        "pair": msg["pair"],
                        "interval": msg["interval"]
                        },
                    "time": msg["time"],#datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),#+'Z',
                    "fields": {
                        "open": float(msg["open"]),
                        "close":float(msg["close"]),
                        "high":float(msg["high"]),
                        "low":float(msg["low"]),
                        "high-low":float(msg["high-low"]),
                        "close-open":float(msg["close-open"]),
                        "volume":float(msg["volume"]), #Base asset volume
                        "number_of_trades":float(msg["number_of_trades"]),
                        "quote_volume":float(msg["quote_volume"]), #Quote asset volume
                        "active_buy_volume":float(msg["active_buy_volume"]), #Taker buy base asset volume
                        "active_buy_quote_volume":float(msg["active_buy_quote_volume"]), #Taker buy quote asset volume
                        "gain":float(msg["gain"]),
                        "lose":float(msg["lose"]),
                        "avg_gain":float(msg["avg_gain"]),
                        "avg_lose":float(msg["avg_lose"]),
                        "RSI":float(msg["RSI"]),
                        "stochRSI":float(msg["stochRSI"]),
                        "highest_high":float(msg["highest_high"]),
                        "lowest_low":float(msg["lowest_low"]),                    
                    
                    }
                }
            ]            
      
        self.InfluxClient.write_points(points=json_body4,retention_policy='coin_policy')
        print("inserting message with time: {0}, message type: {1}, measurement: {2}".format(json_body4[0]["time"],msg_type,measurement))

    def create_msg_from_history(self,event_type,interval,symbol,units,num_of_units,from_now=True,from_date=0,to_date=0): #update this to accept more ranges
    
        #see valid intervals inside the client function
        #implement more ranges not just x amount of hours ago
        
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
   
        list_of_msgs = []
        msg ={}
        msg["k"]={}
        for raw_msg in raw_data:
            
            msg["e"]= event_type
            msg["s"]= symbol      
            msg["k"]["t"]=raw_msg[0]
            msg["k"]["i"]=interval
            msg["k"]["o"]=raw_msg[1]
            msg["k"]["c"]=raw_msg[4]
            print(raw_msg[4])
            msg["k"]["h"]=raw_msg[2]
            msg["k"]["l"]=raw_msg[3]   
            msg["k"]["v"]=raw_msg[5]     
            msg["k"]["n"]=raw_msg[8]      
            msg["k"]["q"]=raw_msg[7]     
            msg["k"]["V"]=raw_msg[9]     
            msg["k"]["Q"]=raw_msg[10] 
            list_of_msgs.append(copy.deepcopy(msg))
        
        return list_of_msgs      

    def insert_offline_data(self,list_of_msgs,measurement,msg_type):   
    
        for msg in list_of_msgs:        
            self.insertMinuteTickValueIntoInfluxDB(msg,measurement,msg_type)
            
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

    def msg_data_RSI_calculation(self,list_of_msgs,list_of_msgs_RSI, window, starting):
        raise Exception("INDICATORS PENDING")  
        #window = 15
        if starting:
            init_msg = list_of_msgs[0]
        else:
            init_msg = list_of_msgs_RSI[0]
            if init_msg['RSI'] < 0:
                raise Exception("not a valis RSI, you must go further back in time")  
        list_new_msgs = []
        count = 0
        
        avg_accum_lose = 0
        avg_accum_gain = 0
        
        
        for msg in list_of_msgs[1:]:
            
            new_msg = copy.deepcopy(msg)
            
            count = count + 1
            new_msg['change']=float(msg['close']-init_msg['close'])
            if new_msg['change']>=0.0:
                new_msg['gain'] = float(new_msg['change'])
                new_msg['lose'] = 0.0
            else:
                new_msg['gain'] = 0.0
                new_msg['lose'] = float(abs(new_msg['change']))
            
            if (count < window+1) and starting:
                avg_accum_lose = avg_accum_lose + new_msg['lose']/float(window)
                avg_accum_gain = avg_accum_gain + new_msg['gain']/float(window)
                new_msg['avg_gain'] = float(avg_accum_gain)
                new_msg['avg_lose'] = float(avg_accum_lose)
            else:
                new_msg['avg_gain'] = (init_msg['avg_gain']*(window-1)+new_msg['gain'])/float(window)
                new_msg['avg_lose'] = (init_msg['avg_lose']*(window-1)+new_msg['lose'])/float(window)
            
            try:
                RS = new_msg['avg_gain']/float(new_msg['avg_lose'])
            except:
                RS = 0
                
            new_msg['RSI'] = 100.0 - 100.0/(1+RS)
            
            init_msg = copy.deepcopy(new_msg)
            list_new_msgs.append(copy.deepcopy(new_msg))     
            
        return list_new_msgs       

    def populate_RSI(self,all_data=True,time_back='10d',msg_type = 'RSI',interval=14):
        raise Exception("INDICATORS PENDING")  
        print('s')
        
        if all_data:
            dataRSI_=[1,1]
            data_test_1=self.InfluxClient.query("select * from offline_minute_tick WHERE pair = '{0}';".format(self.symbol,))
            data_ =list(data_test_1)
            starting = True        
            RSI_list_of_msgs =  self.msg_data_RSI_calculation(data_[0],dataRSI_[0],interval,starting)
            msg_type = 'RSI'
            measurement = 'RSI_offline_minute_tick_test_3'
            self.insert_offline_data(RSI_list_of_msgs,measurement,msg_type)
            
        else:
            starting = False
            dataRSI_=self.InfluxClient.query("select * from RSI_offline_minute_tick WHERE time > now() -{0} AND pair = '{1}';".format(time_back,self.symbol))
            data_test_1=self.InfluxClient.query("select * from offline_minute_tick WHERE time > now() -{0} AND pair = '{1}';".format(time_back,self.symbol))
            data_ =list(data_test_1)
            dataRSI_ =list(dataRSI_)
            msg_type = 'RSI'            
            measurement = 'RSI_offline_minute_tick_test_3'    
            RSI_list_of_msgs =  self.msg_data_RSI_calculation(data_[0],dataRSI_[0],interval,starting)            
            self.insert_offline_data(RSI_list_of_msgs,measurement,msg_type)        



    def websocket_start(self):
        
        self.bm =BinanceSocketManager(self.client)
        self.bm.start_kline_socket( self.symbol, self.online_process_message)
        self.bm.start()
        
    def websocket_close(self):        
        self.bm.close()

#my_binance_influxdb = binanceInfluxdb()
#
#
#my_binance_influxdb.websocket_start()        
#        
#my_binance_influxdb.websocket_close()           
        
        
symbol_1 = "IOTAUSDT"
symbol_2=  "XRPUSDT"        
###        
my_binance_influxdb_1 = binanceInfluxdb(symbol=symbol_1,is_new_db=False,database='binance')
##my_binance_influxdb_1.insert_offline_tick_data(event_type = 'kline',interval ='1m',units = 'month',num_of_units = 6,msg_type = 'raw') 
###           
my_binance_influxdb_2 = binanceInfluxdb(symbol=symbol_2,is_new_db=False,database='binance')
##my_binance_influxdb_2.insert_offline_tick_data(event_type = 'kline',interval ='1m',units = 'month',num_of_units = 6,msg_type = 'raw') 
#
##event_type,interval,units,num_of_units,msg_type
#
#
my_binance_influxdb_2.websocket_start()  
my_binance_influxdb_1.websocket_start() 









    
