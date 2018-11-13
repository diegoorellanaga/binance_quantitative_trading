import yaml
import os
from binance_connection.binance_to_influxdb import BinanceInfluxdb


def main():
    # fetching configuration parameters
    script_dir = os.path.dirname(__file__)
    file_path = os.path.join(script_dir, 'connection_config.yml')
    with open(file_path,'r') as ymlfile:
        config = yaml.load(ymlfile)
        public_key = config['API_keys']['public']
        private_key = config['API_keys']['private']
        crypto_symbol_list = config['connection_settings']['target_cryptos']
        is_first_time = config['connection_settings']['first_time']
        interval = config['connection_settings']['resolution']
        units = config['connection_settings']['units']
        num_of_units = int(config['connection_settings']['num_of_units'])        
    
    connection_list = [None]*len(crypto_symbol_list)    
    
    # we need to create the database
    if is_first_time:
        is_new_db = True
    
    for i, symbol in enumerate(crypto_symbol_list):
        connection_list[i]=BinanceInfluxdb(symbol=symbol,is_new_db=is_new_db,database='binance',api_key=public_key,api_secret=private_key)
        is_new_db = False #They share the database, thus, we need to create it once.
        
        # we populate the database for the first time
        if is_first_time:
            connection_list[i].insert_offline_tick_data(event_type = 'kline',interval =interval, units = units,num_of_units = num_of_units,msg_type = 'raw')
        # we stablish a websocket connection
        connection_list[i].websocket_start()

if __name__ == "__main__":
   main()
