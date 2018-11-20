#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 18:17:17 2018

@author: root
"""

import numpy as np
import matplotlib.pyplot as plt
import datetime
from influxdb import InfluxDBClient
import zulu
from pytz import timezone

import copy


class tensorflow_influxdb():
    def __init__(self, host='localhost', port=8086, database="binance_test_5", measurement = "offline_minute_tick"):
        
        self.host = host
        self.port = port
        self.database = database
        self.measurement = measurement
        self.InfluxClient = InfluxDBClient(host, port)
        self.InfluxClient.switch_database(database)
        
        self.time_first_point_date = list(self.InfluxClient.query("select FIRST(close) from {0};".format(measurement)))[0][0]['time']        
        self.time_last_point_date = list(self.InfluxClient.query("select LAST(close) from {0};".format(measurement)))[0][0]['time'] 
        
        self.time_first_point_unix = datetime.datetime.strptime(self.time_first_point_date, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone('UTC')).timestamp()  #create time object  #tell the object that its TZ is UTC
        self.time_last_point_unix =  datetime.datetime.strptime(self.time_last_point_date, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone('UTC')).timestamp() 
        #1527759000.0   if I add 60 I'm adding 60 seconds
        
        self.base_point_unix_minutes = self.time_first_point_unix       

        self.minutes_passed = 0
        self.first_stream_call = True
        

        
    def get_points_from_Influxdb(self,number,data_to_extract,resolution,unit,start_time,stop_time,only_value=False,both_limits=False):
        #example data=self.InfluxClient.query("select LAST(close), LAST(open), LAST(volume) from offline_minute_tick WHERE time >= '{0}' AND time < '{1}' GROUP BY time({2}m);".format(start_time,stop_time,unit))

        if resolution =="minutes":
            if not both_limits:
                data=self.InfluxClient.query("select {3} from offline_minute_tick WHERE time >= '{0}' AND time < '{1}' GROUP BY time({2}m);".format(start_time,stop_time,unit,data_to_extract))
            else:
                data=self.InfluxClient.query("select {3} from offline_minute_tick WHERE time >= '{0}' AND time <= '{1}' GROUP BY time({2}m);".format(start_time,stop_time,unit,data_to_extract))
               
            data = list(data)[0]
           #     print(len(data))
           #     print(data)
            if len(data) != number:
                raise Exception("amount of minutes points is different from the parameter number")            
        elif resolution == "hours":
            if not both_limits:            
                data=self.InfluxClient.query("select {3} from offline_minute_tick WHERE time >= '{0}' AND time < '{1}' GROUP BY time({2}h);".format(start_time,stop_time,unit,data_to_extract))
            else:
                data=self.InfluxClient.query("select {3} from offline_minute_tick WHERE time >= '{0}' AND time <= '{1}' GROUP BY time({2}h);".format(start_time,stop_time,unit,data_to_extract)) 
                
            data = list(data)[0]
           #     print(len(data))
           #     print(data)
            if len(data) != number:
                raise Exception("amount of hours points is different from the parameter number") 
        elif resolution == "days":
             #   print("inside days")
            if not both_limits:              
                data=self.InfluxClient.query("select {3} from offline_minute_tick WHERE time >= '{0}' AND time < '{1}' GROUP BY time({2}d);".format(start_time,stop_time,unit,data_to_extract))
            else:
                data=self.InfluxClient.query("select {3} from offline_minute_tick WHERE time >= '{0}' AND time <= '{1}' GROUP BY time({2}d);".format(start_time,stop_time,unit,data_to_extract))
            data = list(data)[0]
           #     print(len(data))
           #     print(data)
            if len(data) != number:
                raise Exception("amount of days points is different from the parameter number")         
            
            
        if only_value:
            dictlist =[]
            for dictionary in data:  #if data_to_extract:LAST(close),LAST(open), LAST(volume)  then data format: [close_1,open_1,volume_1,close_2,open_2,volume_2,...,close_14,open_14,volume_14]
                
                for key in dictionary:
                    if key != 'time':
                        temp = dictionary[key]
                        dictlist.append(temp)
            data = dictlist    
            
        return data



    
    def get_data_stream_from_Influxdb(self, points_set_size,time_sets_to_consider,data_to_extract = "LAST(close)" ,only_value=True, single_output_array = True): #parameterized the coin
        #sets_to_consider: ["minutes","hours","days"]
        #points_set_size: [how many units back are we looking, on each time unit]
        try:
            if len(time_sets_to_consider) < 1:
                raise Exception("at least one time measure must be considered") 
            
            if self.first_stream_call:  #random point initialization in a narrow range at the beggining
                self.base_point_unix_minutes = self.base_point_unix_minutes + points_set_size*60*60*24 + np.random.randint(1,10)*60  # I need at least number of days behind to start making the calculations
                self.first_stream_call = False   
            
            
            number = points_set_size
            
            
            unit = 1
            stop_time_minutes = self.base_point_unix_minutes      
            start_time_minutes = stop_time_minutes - number*60
            
            
            if stop_time_minutes > self.time_last_point_unix:
                print("query run out of points: stop_time:{0}, last_point_db:{1}".format(stop_time_minutes,self.time_last_point_unix))
                return [-1]
            
            stop_time_hours = stop_time_minutes-(stop_time_minutes % 3600)  # if I'm in the time 12:34 it is 12 for the hour, not 13
            stop_time_days = stop_time_minutes - (stop_time_minutes % (3600*24)) #same with the day
            
            start_time_hours = stop_time_hours - number*60*60
            start_time_days = stop_time_days - number*60*60*24
            
            
            
            start_time_minutes_string = zulu.parse(start_time_minutes).isoformat()
            start_time_hours_string = zulu.parse(start_time_hours).isoformat()
            start_time_days_string = zulu.parse(start_time_days).isoformat()
            
            stop_time_minutes_string = zulu.parse(stop_time_minutes).isoformat()
            stop_time_hours_string = zulu.parse(stop_time_hours).isoformat()
            stop_time_days_string = zulu.parse(stop_time_days).isoformat()
  
     #   print("inside minutes",stop_time_minutes_string)      
     #   print("inside hours",stop_time_hours_string)
     #   print("inside days",stop_time_days_string)        
        
            if "minutes" in time_sets_to_consider:
                minute_data = self.get_points_from_Influxdb(number,data_to_extract,"minutes",unit,start_time_minutes_string,stop_time_minutes_string,only_value,False)
            else:
                minute_data = []
            if "hours" in time_sets_to_consider:    
                hour_data = self.get_points_from_Influxdb(number,data_to_extract,"hours",unit,start_time_hours_string,stop_time_hours_string,only_value,False)
            else:
                hour_data = []
            if "days" in time_sets_to_consider:  
                day_data = self.get_points_from_Influxdb(number,data_to_extract,"days",unit,start_time_days_string,stop_time_days_string,only_value,False)
            else:
                day_data = []
            
            self.base_point_unix_minutes = self.base_point_unix_minutes + 60
            
            self.minutes_passed = self.minutes_passed +1
            
            if single_output_array:
                return np.hstack((minute_data,hour_data,day_data))
            else:
                return np.asarray([minute_data,hour_data,day_data])
        except:
            #for corrupted data I just give empty list and keep advancing the time
            self.base_point_unix_minutes = self.base_point_unix_minutes + 60
            return []

    def all_at_once(self, coin_id,points_set_size,time_sets_to_consider,point_size,total_points=100000,unit = 1,data_to_extract = "LAST(close)" ,only_value=True, single_output_array = True,same_measure = True,new_measurement = 'something'):
        damage_point =0
        if same_measure:
            measurement = self.measurement
        else:
            measurement = new_measurement 
        
        all_data_minutes = self.InfluxClient.query("select {1} from {3} WHERE time < now() AND pair = '{2}' GROUP BY time({0}m);".format(unit,data_to_extract,coin_id,measurement))
        print("#####################")
       # print(all_data_minutes)      
        all_data_minutes_as_dict_list = list(all_data_minutes)[0]
        
        oldest_time = all_data_minutes_as_dict_list[0]['time']
        oldest_time_unix = self.from_date_to_unix(oldest_time)
        
        if total_points == 0:
            total_points = len(all_data_minutes_as_dict_list)-100 #works with 10000
            print("total_points",total_points)
        number = points_set_size
        #start with a whole day not a fraction
        proposed_init_time_unix = oldest_time_unix + number*60*60*24 + 5*60
        proposed_init_index = 0 + number*60*24 + 5
        
        checking = True
        
        while checking:
        
            if (proposed_init_time_unix % 86400) != 0:
                
                proposed_init_time_unix = proposed_init_time_unix +60
                proposed_init_index = proposed_init_index + 1
                
            else:
                print("final proposed unix time: ",proposed_init_time_unix)
                checking = False
        
        
        init_index = proposed_init_index
        
        
        first_loop = True
        
        is_minute = "minutes" in time_sets_to_consider
        is_hours = "hours" in time_sets_to_consider
        is_days = "days" in time_sets_to_consider
        minutes_data = []
        hours_data = []
        days_data = []
        
        
        if only_value:
            data_point_set = np.zeros([total_points,point_size]) #to include the time I need to set the elements type to np.object ,dtype=np.object)
        else:
            data_point_set = np.zeros([total_points,point_size+points_set_size*1],dtype=np.object)
        
        
        for i in range(total_points):
            if i % 10000 == 0:
                print(i)
        

            if is_minute:          
                minutes_data=all_data_minutes_as_dict_list[init_index-number+i:init_index+i] 
                minutes_dictlist =[]
                for dictionary in minutes_data:  #if data_to_extract:LAST(close),LAST(open), LAST(volume)  then data format: [close_1,open_1,volume_1,close_2,open_2,volume_2,...,close_14,open_14,volume_14]
                    minutes_dictlist.extend(list(dictionary.values())[1*only_value:]) #to debug include the time by removing the 1
                minutes_data = minutes_dictlist               
            
            
            if (i % 60 == 0) and is_hours:
                
                hours_data = all_data_minutes_as_dict_list[init_index-number*60+i:init_index+i:60]
                hours_dictlist =[]
                for dictionary in hours_data:  #if data_to_extract:LAST(close),LAST(open), LAST(volume)  then data format: [close_1,open_1,volume_1,close_2,open_2,volume_2,...,close_14,open_14,volume_14]
                    hours_dictlist.extend(list(dictionary.values())[1*only_value:])
                hours_data = hours_dictlist                  
                
                
                
                
            if (i % 1440 == 0) and is_days:
                
                days_data = all_data_minutes_as_dict_list[init_index-number*1440+i:init_index+i:1440]
                days_dictlist =[]
                for dictionary in days_data:  #if data_to_extract:LAST(close),LAST(open), LAST(volume)  then data format: [close_1,open_1,volume_1,close_2,open_2,volume_2,...,close_14,open_14,volume_14]
                    days_dictlist.extend(list(dictionary.values())[1*only_value:])
                days_data = days_dictlist 
           
            
            
            
            data_point = np.hstack((minutes_data,hours_data,days_data))   
     #       print(data_point.shape)
     #       print(data_point_set[0,:].shape)
            try:
                data_point_set[i,:] = data_point
            except:
                damage_point = damage_point+1
                print("damage_point n:",damage_point)

            
        return data_point_set     

    def all_at_once_fast(self, points_set_size,time_sets_to_consider,point_size,total_points=100000,unit = 1,data_to_extract = "LAST(close)" ,only_value=True, single_output_array = True):
        raise Exception("needs to be updated")
        
        raise Exception("not working") 
        is_minute = "minutes" in time_sets_to_consider
        is_hours = "hours" in time_sets_to_consider
        is_days = "days" in time_sets_to_consider   
        minutes_data = []
        hours_data = []
        days_data = []
        data_point_set = np.zeros([total_points,point_size],dtype=np.object)
        
        
        if is_minute:        
            all_data_minutes = self.InfluxClient.query("select {1} from offline_minute_tick WHERE time < now() GROUP BY time({0}m);".format(unit,data_to_extract))
            all_data_minutes_as_dict_list = list(all_data_minutes)[0]
        if is_hours:
            all_data_hours = self.InfluxClient.query("select {1} from offline_minute_tick WHERE time < now() GROUP BY time({0}h);".format(unit,data_to_extract))
            all_data_hours_as_dict_list = list(all_data_hours)[0]
        if is_days:
            all_data_days = self.InfluxClient.query("select {1} from offline_minute_tick WHERE time < now() GROUP BY time({0}d);".format(unit,data_to_extract))
            all_data_days_as_dict_list = list(all_data_days)[0]            

        
        oldest_minute_time = all_data_minutes_as_dict_list[0]['time']
        oldest_hour_time = all_data_hours_as_dict_list[0]['time']        
        oldest_day_time = all_data_days_as_dict_list[0]['time']        

        
        oldest_minute_time_unix = self.from_date_to_unix(oldest_minute_time)
        oldest_hour_time_unix = self.from_date_to_unix(oldest_hour_time)
        oldest_day_time_unix = self.from_date_to_unix(oldest_day_time) + 24*60*60 #1 day in the future
        
        print(oldest_minute_time_unix,oldest_hour_time_unix,oldest_day_time_unix)
        step_forward_minutes=(oldest_day_time_unix - oldest_minute_time_unix)/60.0
        step_forward_hours=(oldest_day_time_unix - oldest_hour_time_unix)/(60.0*60.0)
        step_forward_days=(oldest_day_time_unix - oldest_day_time_unix)/1        
        
        init_index_minute = step_forward_minutes + points_set_size*1440
        init_index_hours = step_forward_hours +points_set_size*24
        init_index_days = step_forward_days + points_set_size*1
        #19590.0 -204.0 14.0
        print(init_index_minute,init_index_hours,init_index_days)
        
        h=0
        d=0
        
        for i in range(total_points):
            if i % 10000 == 0:
                print(i)            
            
            minutes_data=all_data_minutes_as_dict_list[int(init_index_minute-points_set_size+i):int(init_index_minute+i)]
            minutes_dictlist =[]
            for dictionary in minutes_data:  #if data_to_extract:LAST(close),LAST(open), LAST(volume)  then data format: [close_1,open_1,volume_1,close_2,open_2,volume_2,...,close_14,open_14,volume_14]
                minutes_dictlist.extend(list(dictionary.values())[:])
            minutes_data = minutes_dictlist             
            
            if (i % 60 == 0) and is_hours:
                
                hours_data = all_data_hours_as_dict_list[int(init_index_hours-points_set_size+h):int(init_index_hours+h)]
                hours_dictlist =[]
                for dictionary in hours_data:  #if data_to_extract:LAST(close),LAST(open), LAST(volume)  then data format: [close_1,open_1,volume_1,close_2,open_2,volume_2,...,close_14,open_14,volume_14]
                    hours_dictlist.extend(list(dictionary.values())[:])
                hours_data = hours_dictlist                  
                h=h+1 
                
                
                
            if (i % 1440 == 0) and is_days:
                
                days_data = all_data_days_as_dict_list[int(init_index_days-points_set_size+d):int(init_index_days+d)]
                days_dictlist =[]
                for dictionary in days_data:  #if data_to_extract:LAST(close),LAST(open), LAST(volume)  then data format: [close_1,open_1,volume_1,close_2,open_2,volume_2,...,close_14,open_14,volume_14]
                    days_dictlist.extend(list(dictionary.values())[:])
                days_data = days_dictlist
                d=d+1
            
            data_point = np.hstack((minutes_data,hours_data,days_data))   
            
            data_point = np.hstack((minutes_data,hours_data,days_data))   
            print(data_point_set[i,:])
            print(data_point.shape)
            data_point_set[i,:] = data_point
                
            
        return data_point_set 

                 
    def from_date_to_unix(self,date_string,date_format = "%Y-%m-%dT%H:%M:%SZ",time_zone = "UTC"):
        unix_time_utc = datetime.datetime.strptime(date_string, "{0}".format(date_format)).replace(tzinfo=timezone(time_zone)).timestamp()
        return unix_time_utc
        
    def from_unix_to_date(self,date_unix, with_Z = True): 
        string_date = zulu.parse(date_unix).isoformat()  
        if with_Z:  
            string_date=string_date.replace(string_date[-6:],'Z')
        
        return string_date
            
    
    def reset_stream_from_Influxdb(self):
        print("data stream has been reset to time: {0}".format(self.time_first_point_unix ))
        self.base_point_unix_minutes = self.time_first_point_unix   
        self.first_stream_call = True
        
        
        
        
#all_at_once(self, coin_id,points_set_size,time_sets_to_consider,point_size,total_points=200000,unit = 1,data_to_extract = "LAST(close),LAST(volume),LAST(number_of_trades)" ,only_value=True, single_output_array = True,same_measure = True,new_measurement = 'something'):        
        
        
#tf_influxdb_1 = tensorflow_influxdb(host='localhost', port=8086,database="binance", measurement="minute_tick")
#
#
#data_test_1 =  tf_influxdb_1.all_at_once(coin_id="IOTAUSDT",points_set_size=1,time_sets_to_consider=["minutes"],point_size=1*1*3,total_points=0,only_value=True,unit = 1,data_to_extract="LAST(close),LAST(volume),LAST(number_of_trades)")


#data_test_2 =  tf_influxdb_1.all_at_once(coin_id="IOTAUSDT",points_set_size=14,time_sets_to_consider=["minutes"],point_size=1*14*2,total_points=100000,only_value=False,unit = 1,data_to_extract="LAST(close),LAST(volume)")


#data_test_1 = tf_influxdb_1.all_at_once("IOTAUSDT",14,["minutes"],14*1*2,100000,1,"LAST(close),LAST(volume)",)
##
#np.save("/home/diego/Desktop/crypto/rl-crypto/Data/iota-vol-ntrade-close.npy", data_test_1[:-2210,:])    


    
#  
#data = np.load("/home/diego/Desktop/crypto/rl-crypto/Data/minutes_14_close_volume_100000.npy")       
#data = np.load("/home/diego/Desktop/crypto/rl-crypto/Data/minutes_1_close_volume_100000.npy")        

#
#import numpy as np
#x = np.array([[1,2,3], [4,5,np.nan], [7,8,9], [True, False, True]])
#print("Original array:")
#print(x)
#print("Remove all non-numeric elements of the said array")
#print(x[~np.isnan(x).any(axis=1)])
#






class data_handling():
    def __init__(self,data,name='something'):
        #assuming data is a numpyr array
        self.name = name
        self.data = data
        self.counter = 0
        self.data_shape = self.data.shape
        self.random_index = 0
        self.is_none_removed = False
        
    def remove_none_rows(self):
        self.is_none_removed = True
        self.data = self.data[~np.isnan(self.data).any(axis=1)]
        self.data_shape = self.data.shape
        
        
    def get_next_point_stream(self):

        point_to_return = self.data[self.counter,:]
        self.counter = self.counter + 1
        return point_to_return

        
    def reset_stream(self):
        self.set_random_init_index()
        

    def get_random_point(self):
        
        self.random_index = np.random.randint(0,int(self.data_shape[0]))
        return self.data[self.random_index,:]
        
    def set_random_init_index(self):
        self.counter = np.random.randint(0,int(self.data_shape[0]/2.0))
        print("###################################")
        print("###################################")
        print("INIT POINT: ",self.counter)
        
    def normalize_data(self,num_measurements):
        if not self.is_none_removed:
            raise Exception("remove none first")  
        
        temp_data = copy.deepcopy(self.data)
        
        #currently working for close,volume minute hours
        two_mes_lim = int(self.data_shape[1]/2)
        inside_lim = int(self.data_shape[1]/4)
        #make this function parametric
        for i in range(self.data_shape[0]):
            
#            print(self.data_shape)
#            print(int(self.data_shape[1]/2))
#            print(len(temp_data[i,:][0::2]))
#            print(len(temp_data[i,:][1::2]))            
            self.data[i,:inside_lim]= (temp_data[i,:two_mes_lim][0::2]-np.min(temp_data[i,:two_mes_lim][0::2]))/np.max(temp_data[i,:two_mes_lim][0::2]-np.min(temp_data[i,:two_mes_lim][0::2])+0.0001)+0.001
            self.data[i,inside_lim:2*inside_lim]= (temp_data[i,:two_mes_lim][1::2]-np.min(temp_data[i,:two_mes_lim][1::2]))/np.max(temp_data[i,:two_mes_lim][1::2]-np.min(temp_data[i,:two_mes_lim][1::2])+0.0001)+0.001

            self.data[i,2*inside_lim:3*inside_lim]= (temp_data[i,two_mes_lim:][0::2]-np.min(temp_data[i,two_mes_lim:][0::2]))/np.max(temp_data[i,two_mes_lim:][0::2]-np.min(temp_data[i,two_mes_lim:][0::2])+0.0001)+0.001
            self.data[i,3*inside_lim:4*inside_lim]= (temp_data[i,two_mes_lim:][1::2]-np.min(temp_data[i,two_mes_lim:][1::2]))/np.max(temp_data[i,two_mes_lim:][1::2]-np.min(temp_data[i,two_mes_lim:][1::2])+0.0001)+0.001
         
        
        


#
#data = np.load("/home/diego/Desktop/crypto/rl-crypto/Data/minutes_hours_14_close_volume_100000_all_at_once.npy") 
#
#
#
#hhh = data_handling(data)
#
#hhh.remove_none_rows()
#hhh.normalize_data(2)


#np.save("/home/diego/Desktop/crypto/rl-crypto/Data/minutes_hours_days_14_close_volume_number_of_trades_100000_all_at_once_fast", data_test_2)            
        
        

#plt.plot(data_test_1[:60000,49],'r')        
#plt.show()
#
#plt.plot(data_test_2[:60000,49],'k')        
#plt.show()        
        
#0,56,112

#DO THE TEST WITH THE NEW DATABASE, PROBABLY TE OLD DATABASE IS CORRUPTED
        

'''
1526594460.0 1526594400.0 1526601600.0
20279.0 456.0 14.0
0
Traceback (most recent call last):

  File "<ipython-input-8-3270e4aae35b>", line 1, in <module>
    data_test_2 = tf_influxdb_1.all_at_once_fast(14,["minutes","hours","days"],14*3*3,100000,1,"LAST(close),LAST(volume),LAST(number_of_trades)")

  File "/home/diego/Desktop/Study/RL/projects/crypto_data_pipeline.py", line 295, in all_at_once_fast
    minutes_data=all_data_minutes_as_dict_list[init_index_minute-points_set_size+i:init_index_minute+i]

TypeError: slice indices must be integers or None or have an __index__ method
'''        
        
        
        
        
       
        
        
        
        
        
        
        