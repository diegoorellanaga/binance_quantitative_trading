#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 18:17:17 2018

@author: root
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
from influxdb import InfluxDBClient
import zulu
from pytz import timezone

import copy


class InfluxdbDataExtraction():
    def __init__(self, host='localhost', port=8086, database="binance"):
        
        self.host = host
        self.port = port
        self.database = database
        self.InfluxClient = InfluxDBClient(host, port)
        self.InfluxClient.switch_database(database)
            
    def extract_data_basic(self, coin_id,measurement = "minute_tick",unit = "1h",data_to_extract = ["close","volume","number_of_trades"]):
        
        data_to_extract_string = self.list_to_string(data_to_extract)
        data_influxdb = self.InfluxClient.query("select {1} from {3} WHERE time < now() AND pair = '{2}' GROUP BY time({0});".format(unit,data_to_extract_string,coin_id,measurement))
        data_to_extract.append("time")
        df = pd.DataFrame(data = list(data_influxdb)[0])
        df.columns = data_to_extract        
        return df

                 
    def from_date_to_unix(self,date_string,date_format = "%Y-%m-%dT%H:%M:%SZ",time_zone = "UTC"):
        unix_time_utc = datetime.datetime.strptime(date_string, "{0}".format(date_format)).replace(tzinfo=timezone(time_zone)).timestamp()
        return unix_time_utc
        
    def from_unix_to_date(self,date_unix, with_Z = True): 
        string_date = zulu.parse(date_unix).isoformat()  
        if with_Z:  
            string_date=string_date.replace(string_date[-6:],'Z')
        
        return string_date
            
    
    def list_to_string(self,list_param):
        final_string =""
        for i,word in enumerate(list_param):
            final_string = final_string+"LAST("+word+"),"
        return final_string[:-1]  
        




        
#extract_data_m_h_d(self, coin_id,points_set_size,time_sets_to_consider,point_size,total_points=200000,unit = 1,data_to_extract = "LAST(close),LAST(volume),LAST(number_of_trades)" ,only_value=True, single_output_array = True,same_measure = True,new_measurement = 'something'):        
        
        
#tf_influxdb_1 = InfluxdbDataExtraction(host='localhost', port=8086,database="binance")
#

#data_basic = tf_influxdb_1.extract_data_basic(coin_id = "BTCUSDT", unit = "1h",data_to_extract = ["close"], measurement ="minute_tick" )






        
        
        