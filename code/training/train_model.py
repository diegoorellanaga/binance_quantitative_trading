import pandas as pd
import numpy as np
from math import sqrt
from numpy import concatenate
from matplotlib import pyplot
from pandas import read_csv
from pandas import DataFrame
from pandas import concat
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.models import model_from_json
from keras.layers import Dropout
from keras.layers import Flatten
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
from training.extract_data import InfluxdbDataExtraction

class TrainModel():
    def __init__(self,raw_data,name="train_1", dataFrame = False):
        
        if dataFrame:
            self.raw_data = raw_data.values
            self.columns = raw_data.columns
        else:        
            self.raw_data = raw_data
            self.name=name
        
    def series_to_supervised(self,data, n_in=1, n_out=1, dropnan=True):
        	n_vars = 1 if type(data) is list else data.shape[1]
        	df = DataFrame(data)
        	cols, names = list(), list()
        	# input sequence (t-n, ... t-1)
        	for i in range(n_in, 0, -1):
        		cols.append(df.shift(i))
        		names += [('var%d(t-%d)' % (j+1, i)) for j in range(n_vars)]
        	# forecast sequence (t, t+1, ... t+n)
        	for i in range(0, n_out):
        		cols.append(df.shift(-i))
        		if i == 0:
        			names += [('var%d(t)' % (j+1)) for j in range(n_vars)]
        		else:
        			names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]
        	# put it all together
        	agg = concat(cols, axis=1)
        	agg.columns = names
        	# drop rows with NaN values
        	if dropnan:
        		agg.dropna(inplace=True)
        	return agg        
              
    def get_raw_data_shape(self):
        
        return self.raw_data.shape
        
    def create_data_frame(self,columns):
        
        self.df_data = pd.DataFrame(data=self.raw_data,columns = columns)  
        
    def drop_nan_rows(self):

        self.df_data.dropna(inplace=True)            

    def scale_data(self,tuple_limit):

        self.scaler  = MinMaxScaler(feature_range=tuple_limit)
        self.scaled_data = self.scaler.fit_transform(self.df_data)
        
    def diff_data(self,periods = 1):

        self.df_data = self.df_data.diff(periods = periods) 
        
    def create_labels(self, tolerance = 0.004):
        #tolerance goes between 0.002 and 1. 0.002 is the minimun for a 1% fee, fee for selling and fee for buying and viceversa
        train_limit = self.train_X.shape[0]
        
        self.y_train_labels = np.zeros([train_limit,3]) 
        
        for i in range(train_limit):
            close_t_minus_1 = self.train_X[i,-self.num_features]
            
            
            
            future_close_prices = self.train_y[i,:]
            min_future_close_price = min(future_close_prices)
            max_future_close_price = max(future_close_prices)
            scenario_1_potential = abs(close_t_minus_1-max_future_close_price)
            scenario_2_potential = abs(close_t_minus_1-min_future_close_price)
            is_scenario_1_worth = max_future_close_price*(1-tolerance) > close_t_minus_1
            is_scenario_2_worth = close_t_minus_1*(1-tolerance) > min_future_close_price
            is_scenario_1 = scenario_1_potential > scenario_2_potential
            is_scenario_2 = scenario_2_potential > scenario_1_potential
            
            if is_scenario_1 and is_scenario_1_worth:
                self.y_train_labels[i,:] = np.asarray([1,0,0]) 
                
                
            elif is_scenario_2 and is_scenario_2_worth:
                self.y_train_labels[i,:] = np.asarray([0,1,0]) 
                
            else:
                self.y_train_labels[i,:] = np.asarray([0,0,1]) 

        ####################### test data #################################
            
        test_limit = self.test_X.shape[0]
        
        self.y_test_labels = np.zeros([test_limit,3]) 
        
        for i in range(test_limit):
            close_t_minus_1 = self.test_X[i,-self.num_features]
            future_close_prices = self.test_y[i,:]
            min_future_close_price = min(future_close_prices)
            max_future_close_price = max(future_close_prices)
            scenario_1_potential = abs(close_t_minus_1-max_future_close_price)
            scenario_2_potential = abs(close_t_minus_1-min_future_close_price)
            is_scenario_1_worth = max_future_close_price*(1-tolerance) > close_t_minus_1
            is_scenario_2_worth = close_t_minus_1*(1-tolerance) > min_future_close_price
            is_scenario_1 = scenario_1_potential > scenario_2_potential
            is_scenario_2 = scenario_2_potential > scenario_1_potential
            
            if is_scenario_1 and is_scenario_1_worth:
                self.y_test_labels[i,:] = np.asarray([1,0,0]) 
                
                
            elif is_scenario_2 and is_scenario_2_worth:
                self.y_test_labels[i,:] = np.asarray([0,1,0]) 
                
            else:
                self.y_test_labels[i,:] = np.asarray([0,0,1]) 


    def encode_column(self,column):
        
        encoder = LabelEncoder()
        
        self.raw_data[:,column] = encoder.fit_transform(self.raw_data[:,column])
        
        

    def shift_data(self,past_units,future_units,num_features,position_feature):
        self.n_obs = num_features*past_units        
        self.position_feature = position_feature
        self.num_features = num_features
        self.past_units = past_units
        self.future_units = future_units

        self.reframed_scaled_df_data = self.series_to_supervised(self.scaled_data, past_units, future_units)
        print(self.reframed_scaled_df_data.head())


    def split_data_train_test(self,train_percent):
        
        try:
            
            limit = self.reframed_scaled_df_data.shape[0]        
            self.training_amount = int(limit*train_percent)
            reframed_scaled_data=self.reframed_scaled_df_data.values                
            self.train_data = reframed_scaled_data[:self.training_amount, :]
            self.test_data = reframed_scaled_data[self.training_amount:, :]  
        except:
            
            print("we work with reframed_scaled_df_data")              
                
    def split_data_x_y(self,predict_present = False):

        self.predict_present = predict_present
        if self.predict_present:
            print(self.train_data[:, :self.n_obs].shape)
            print(self.test_data[:, :self.n_obs].shape)            
            self.train_X, self.train_y = self.train_data[:, :self.n_obs], self.train_data[:, self.n_obs-self.num_features+self.position_feature::self.num_features] #we need to jump the number of features as they are intercalated
            self.test_X, self.test_y = self.test_data[:, :self.n_obs], self.test_data[:, self.n_obs-self.num_features+self.position_feature::self.num_features]
            self.train_X_LSTM = self.train_X.reshape((self.train_X.shape[0], self.past_units, self.num_features))
            self.test_X_LSTM = self.test_X.reshape((self.test_X.shape[0], self.past_units, self.num_features))

            
            
        else:
            self.train_X, self.train_y = self.train_data[:, :self.n_obs], self.train_data[:, self.n_obs+self.position_feature::self.num_features] #we need to jump the number of features as they are intercalated
            self.test_X, self.test_y = self.test_data[:, :self.n_obs], self.test_data[:, self.n_obs+self.position_feature::self.num_features]
            self.train_X_LSTM = self.train_X.reshape((self.train_X.shape[0], self.past_units, self.num_features))
            self.test_X_LSTM = self.test_X.reshape((self.test_X.shape[0], self.past_units, self.num_features))
 
            print(self.train_X_LSTM.shape, self.train_y.shape, self.test_X_LSTM.shape, self.test_y.shape)

    def train_model_regression_LSTM(self,hidden_neurons=50, epochs=50, batch_size=100, dropout = False):
        
        self.model = Sequential()
        self.model.add(LSTM(hidden_neurons, input_shape=(self.train_X_LSTM.shape[1], self.train_X_LSTM.shape[2])))
        if dropout:
            self.model.add(Dropout(0.2))
        if self.predict_present:
            self.model.add(Dense(self.future_units+1))
        else:
            self.model.add(Dense(self.future_units))
        self.model.compile(loss='mae', optimizer='adam')
        self.history = self.model.fit(self.train_X_LSTM, self.train_y, epochs=epochs, batch_size=batch_size, validation_data=(self.test_X_LSTM, self.test_y), verbose=2, shuffle=False)
        pyplot.plot(self.history.history['loss'], label='train')
        pyplot.plot(self.history.history['val_loss'], label='test')
        pyplot.legend()
        pyplot.show()

    def train_model_simple_classifier_DENSE(self,layers = [50], epochs = 50 , batch_size = 100):
        
        self.model = Sequential()
        
        for i in range(len(layers)):
            if i == 0:
                self.model.add(Flatten(input_shape = (self.train_X_LSTM.shape[1], self.train_X_LSTM.shape[2]) ))
                self.model.add(Dense(layers[i],activation='relu'))
            else:
                self.model.add(Dense(layers[i],activation = 'relu'))
        self.model.add(Dense(3, activation='softmax'))
	    # Compile model
        self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        self.history = self.model.fit(self.train_X_LSTM, self.y_train_labels, epochs=epochs, batch_size = batch_size, validation_data = (self.test_X_LSTM, self.y_test_labels), verbose=2, shuffle = True)
        pyplot.plot(self.history.history['acc'], label='train')
        pyplot.plot(self.history.history['val_acc'], label='test')
        pyplot.legend()
        pyplot.show()	              
                        
    def train_model_simple_classifier_LSTM(self,layers = [50], epochs = 50 , batch_size = 100):
        
        self.model = Sequential()
        
        for i in range(len(layers)):
            if i == 0:
                self.model.add(LSTM(layers[i], input_shape=(self.train_X_LSTM.shape[1], self.train_X_LSTM.shape[2])))
            else:
                self.model.add(Dense(layers[i],activation = 'relu'))
        self.model.add(Dense(3, activation='softmax'))
	    # Compile model
        self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        self.history = self.model.fit(self.train_X_LSTM, self.y_train_labels, epochs=epochs, batch_size = batch_size, validation_data = (self.test_X_LSTM, self.y_test_labels), verbose=2, shuffle = True)
        pyplot.plot(self.history.history['acc'], label='train')
        pyplot.plot(self.history.history['val_acc'], label='test')
        pyplot.legend()
        pyplot.show()                
        
        
        

    def save_model(self,path_model,path_weigths,model_id):

        # serialize model to JSON
        model_json = self.model.to_json()
        with open(path_model+"model_{0}.json".format(model_id), "w") as json_file:
            json_file.write(model_json)
        # serialize weights to HDF5
        self.model.save_weights(path_weigths+"model_{0}.h5".format(model_id))
        print("Saved model to disk")        

    def load_model(self,path_model,path_weigths,model_id):

        # load json and create model
        json_file = open(path_model+'model_{0}.json'.format(model_id), 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.model = model_from_json(loaded_model_json)
        # load weights into new model
        self.model.load_weights(path_weigths+"model_{0}.h5".format(model_id))
        print("Loaded model from disk")

    def get_predicted_data(self):
        self.yhat_test = self.model.predict(self.test_X_LSTM)
        self.yhat_train = self.model.predict(self.train_X_LSTM)        

    def invert_scale_prediction(self,):
        if self.predict_present:
            offset = 0
        else: 
            offset = 1
            
            
        self.columns_stack_test = self.yhat_test[:-1,1-offset]
        self.columns_stack_train = self.yhat_train[:-1,1-offset]         
      
        
        for i in range(self.num_features-1):
            
            self.columns_stack_test = np.column_stack((self.columns_stack_test,self.test_X[1:,-self.num_features+i+1]))
            self.columns_stack_train = np.column_stack((self.columns_stack_train,self.train_X[1:,-self.num_features+i+1]))            
        if self.num_features < 2:
            
            self.columns_stack_test = np.expand_dims(self.columns_stack_test, axis=1)
            self.columns_stack_train = np.expand_dims(self.columns_stack_train, axis=1)
            
            self.original_scale_test_last = self.scaler.inverse_transform(self.columns_stack_test)
            self.original_scale_train_last = self.scaler.inverse_transform(self.columns_stack_train)         
        else:
            self.original_scale_test_last = self.scaler.inverse_transform(self.columns_stack_test)
            self.original_scale_train_last = self.scaler.inverse_transform(self.columns_stack_train)  

    def plotPredictedOriginal(self):

        pyplot.plot(self.train_X_LSTM[1:,-1,0],'k')
        pyplot.plot(self.yhat_train[:-1,0],'b')
        pyplot.show()

        print(self.original_scale_test_last[:].shape)
        
        pyplot.plot(self.original_scale_test_last[:,0],'b')
        pyplot.plot(self.raw_data[self.training_amount:,0],'k')
        pyplot.show()  
        
        pyplot.plot(self.original_scale_train_last[:,0],'b')
        pyplot.plot(self.raw_data[:self.training_amount,0],'k')
        pyplot.show()  


        
    def drop_column(self,column_name):
        
        self.df_data=self.df_data.drop([column_name],axis=1)




#tf_influxdb_1 = InfluxdbDataExtraction(host='localhost', port=8086,database="binance")
##
#
#data_basic = tf_influxdb_1.extract_data_basic(coin_id = "BTCUSDT", unit = "1h",data_to_extract = ["close",'volume'], measurement ="minute_tick" )
#
#
#
#LSTM_1 = TrainModel(raw_data=data_basic,name = "test_1",dataFrame= True)
#LSTM_1.create_data_frame(columns=LSTM_1.columns)
#LSTM_1.drop_nan_rows()
#LSTM_1
##LSTM_1.diff_data()
##LSTM_1.drop_nan_rows()
#LSTM_1.drop_column('time')
#LSTM_1.scale_data(tuple_limit = (0,1))
#LSTM_1.shift_data(past_units = 14,future_units = 5,num_features = 2,position_feature = 0)
#LSTM_1.split_data_train_test(0.8)
#LSTM_1.split_data_x_y(predict_present = True)
#LSTM_1.train_model_regression_LSTM(hidden_neurons=80,epochs=20,batch_size=72, dropout = True)
#LSTM_1.save_model(path_model="",path_weigths="",model_id="14-5-1-drop02-present_prediction_80-50-72_3")
##LSTM_1.load_model(path_model="",path_weigths="",model_id="drop_diff_4")
#LSTM_1.get_predicted_data()
#LSTM_1.invert_scale_prediction()
#LSTM_1.plotPredictedOriginal()
##pyplot.plot(LSTM_1.df_data.values[:,0])
##LSTM_1.df_data.shape
#
##train_X_LSTM
#plt.plot(LSTM_1.yhat_train[:,5])
#plt.plot(LSTM_1.train_X_LSTM[:,-3,0])
#plt.show()
#
#plt.plot(LSTM_1.yhat_train[0:100,5])
#plt.plot(LSTM_1.yhat_train[5:105,0])
#plt.show()
#
#
#plt.plot(LSTM_1.yhat_train[5:105,5])
#plt.plot(LSTM_1.yhat_train[5:105,0])
#plt.show()
#
#index = np.random.randint(0,1000)
#plt.plot(LSTM_1.yhat_train[index,:],'b')
##plt.plot(LSTM_1.yhat_train[index:5+index,0],'k')
#plt.show()
#LSTM_1.yhat_train[index,:]
#
#



##size of training set
#n_train_hours = 365 * 24
##3 hours in the past
#n_hours = 3
#n_features = 8
#    
##column to encode = 4
#
#dataset = read_csv('pollution.csv', header=0, index_col=0)
#data_pollution = dataset.values        
#
##-----------------testing-------------------------------
#
#LSTM_1 = TrainModel(raw_data=data_pollution,name = "test_1")
#LSTM_1.encode_column(4)
#LSTM_1.create_data_frame(columns=dataset.columns)
#LSTM_1.drop_nan_rows()
###LSTM_1.diff_data()
###LSTM_1.drop_nan_rows()
#LSTM_1.scale_data(tuple_limit = (0,1))
#LSTM_1.shift_data(past_units = 8,future_units = 5,num_features = 8,position_feature = 0)
#LSTM_1.split_data_train_test(0.8)
#LSTM_1.split_data_x_y()
#LSTM_1.create_labels(tolerance = 0.01)
##LSTM_1.train_model_simple_classifier_DENSE(layers=[50,20],epochs=100,batch_size=72)
#LSTM_1.train_model_simple_classifier_LSTM(layers = [50,5,5],epochs = 50, batch_size= 72)
#
##LSTM_1.save_model(path_model="",path_weigths="",model_id="drop_80n_all_data_close_volume_n_trades_28_10")
###LSTM_1.load_model(path_model="",path_weigths="",model_id="drop_diff_4")
#LSTM_1.get_predicted_data()
#LSTM_1.invert_scale_prediction()
#LSTM_1.plotPredictedOriginal()
###pyplot.plot(LSTM_1.df_data.values[:,0])
###LSTM_1.df_data.shape





#-------------------------------------------------------

        
'''
#/minutes_1_close_volume_number_of_trades_all_points
#data_coin = np.load("/home/diego/Desktop/crypto/rl-crypto/Data/minutes_1_close_volume_100000.npy")  
#data_coin = np.load("/home/diego/Desktop/crypto/rl-crypto/Data/minutes_1_close_volume_number_of_trades_all_points.npy") 
data_coin = np.load("/home/diego/Desktop/crypto/rl-crypto/Data/iota-vol-ntrade-close.npy") 

#--------------------LSTM regression ----------------

LSTM_1 = TrainModel(raw_data=data_coin,name = "test_1")
LSTM_1.create_data_frame(columns=["close","volume","trades_amount"])
LSTM_1.drop_nan_rows()
#LSTM_1.diff_data()
#LSTM_1.drop_nan_rows()
LSTM_1.scale_data(tuple_limit = (0,1))
LSTM_1.shift_data(past_units = 14,future_units = 5,num_features = 3,position_feature = 0)
LSTM_1.split_data_train_test(0.8)
LSTM_1.split_data_x_y(predict_present = True)
LSTM_1.train_model_regression_LSTM(hidden_neurons=80,epochs=20,batch_size=72)
LSTM_1.save_model(path_model="",path_weigths="",model_id="14-5-3-drop02-present_prediction_80-50-72_2")
#LSTM_1.load_model(path_model="",path_weigths="",model_id="drop_diff_4")
LSTM_1.get_predicted_data()
LSTM_1.invert_scale_prediction()
LSTM_1.plotPredictedOriginal()
#pyplot.plot(LSTM_1.df_data.values[:,0])
#LSTM_1.df_data.shape

#train_X_LSTM
plt.plot(LSTM_1.yhat_train[:,5])
plt.plot(LSTM_1.train_X_LSTM[:,-3,0])
plt.show()

plt.plot(LSTM_1.yhat_train[0:100,5])
plt.plot(LSTM_1.yhat_train[5:105,0])
plt.show()


plt.plot(LSTM_1.yhat_train[5:105,5])
plt.plot(LSTM_1.yhat_train[5:105,0])
plt.show()

index = np.random.randint(0,1000)
plt.plot(LSTM_1.yhat_train[index,:],'b')
#plt.plot(LSTM_1.yhat_train[index:5+index,0],'k')
plt.show()
LSTM_1.yhat_train[index,:]
'''
#------------------classifier-------------------------
'''

CLASS_1 = TrainModel(raw_data=data_coin,name = "test_2")
CLASS_1.create_data_frame(columns=["close","volume","trades_amount"])
CLASS_1.drop_nan_rows()
CLASS_1.scale_data(tuple_limit = (0,1))
CLASS_1.shift_data(past_units = 28,future_units = 10 ,num_features = 3,position_feature = 0)
CLASS_1.split_data_train_test(0.6)
CLASS_1.split_data_x_y()
CLASS_1.create_labels(tolerance = 0.00002)



CLASS_1.train_model_simple_classifier_DENSE(layers = [50,10],epochs = 50, batch_size= 100)


'''


#----------------classifier-LSTM--------------------
'''
CLASS_1 = TrainModel(raw_data=data_coin,name = "test_2")
CLASS_1.create_data_frame(columns=["close","volume"])
CLASS_1.drop_nan_rows()
CLASS_1.scale_data(tuple_limit = (0,1))
CLASS_1.shift_data(past_units = 28,future_units = 5 ,num_features = 2,position_feature = 0)
CLASS_1.split_data_train_test(0.6)
CLASS_1.split_data_x_y()
CLASS_1.create_labels(tolerance = 0.002)



CLASS_1.train_model_simple_classifier_LSTM(layers = [50,10],epochs = 10, batch_size= 72)
'''



#LSTM_1.get_predicted_data()
#LSTM_1.yhat_test.shape
#
#series=LSTM_1.df_data
#diff = series.diff()
#pyplot.plot(diff.values[:,0])
#pyplot.show()
#
#diff_back = diff.cumsum(axis=0)
#pyplot.plot(diff_back.values[:,1])
#pyplot.show()
#
#pyplot.plot(series.values[:,0])
#pyplot.show()
#
#pyplot.plot(LSTM_1.yhat_train[:,4])
#pyplot.show()
#
#pyplot.plot(LSTM_1.train_X[:,0])
#pyplot.show()
#LSTM_1.test_X.shape
#type(LSTM_1.test_X[:,0])
#
#
#pyplot.plot(LSTM_1.original_test[:,0])
#pyplot.show()
#
#pyplot.plot(LSTM_1.original_train[:,0])
#pyplot.show()
#LSTM_1.invert_scale_prediction()
#
#
#hstack = np.hstack((LSTM_1.original_train[:,0],LSTM_1.original_test[:,0]))
#
#pyplot.plot(series.values[:,1])
#pyplot.plot(hstack)
#pyplot.show()
#
### make a prediction
### the shape is (num_of_points, num_future_predictions)
##yhat_coin = model_coin.predict(test_X_coin)
##test_X_coin = test_X_coin.reshape((test_X_coin.shape[0], n_features*n_minutes_past)) #(n_hours*n_features)
### invert scaling for forecast
##inv_yhat_coin = concatenate((yhat_coin[:-n_minutes_future,0:1], test_X_coin[n_minutes_future:, -1:]), axis=1) #-1 = (n_features - n_predicted) # I want the volume on time t from the test_X
##inv_yhat_coin = scaler.inverse_transform(inv_yhat_coin)                       # we are selection volume we want to rebuild the (100000,2) orig data
##inv_yhat_coin = inv_yhat_coin[:,0]
### invert scaling for actual
###test_y_coin = test_y_coin.reshape((len(test_y_coin[:,-1]), 1))
##inv_y_coin = concatenate((test_y_coin[:-n_minutes_future,-1:], test_X_coin[n_minutes_future:, -1:]), axis=1)
##inv_y_coin = scaler.inverse_transform(inv_y_coin)
##inv_y_coin = inv_y_coin[:,0]
### calculate RMSE
##rmse_coin = sqrt(mean_squared_error(inv_y_coin, inv_yhat_coin))
##print('Test RMSE: %.3f' % rmse_coin)
##pyplot.plot(inv_yhat_coin[40:560], label='predicted_coin',color='b',linestyle='--')
##pyplot.plot(inv_y_coin[40:560], label='test_coin',color='r',linestyle='-')
##pyplot.legend()
##pyplot.show()
#
#
#
#
#
#
#
#aacols = ['A', 'B','C']
#aadata = pd.DataFrame(np.array([[2,8,9],[1.02,1.2,3],[1.5,1.3,2],[1.998,7.992,4]]),columns=aacols)
#
#aascaler = MinMaxScaler(feature_range = (0,1))
#aascaled_data = aascaler.fit_transform(aadata[aacols])
#
#ggg= np.asarray([[1,1,1],[0.48,0.99,0.2]])
#
#print(aascaled_data)
#aascaler.inverse_transform(ggg)  #it remembers!!!! it remembers the number that need to multiply
#
#
#
#
#








