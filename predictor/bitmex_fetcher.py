import os
import logging
import pandas as pd
import math
import os.path
from bitmex import bitmex
# from binance.client import Client
from datetime import timedelta
from dateutil import parser
from tqdm import tqdm   # (Optional, used for progress-bars)
from creator import preprocess, create_dataset
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class BitmexDataset:
    BINSIZES = {
        "1m": 1,
        "5m": 5,
        "1h": 60,
        "1d": 1440
    }

    def __init__(self, cfg):
        self.cfg = cfg
        self.api_key = os.getenv('BITMEX_API_KEY')
        self.api_secret = os.getenv('BITMEX_API_SECRET')
        self.bitmex_client = bitmex(
            test=False,
            api_key=self.api_key,
            api_secret=self.api_secret
        )
        self.args = cfg['dataset_loader']
        self.batch_size = self.args['batch_size']
        self.symbol = self.args['symbol']
        self.bin = self.args['binsize']
        self.window_size = self.args['window_size']
        self.features = self.args['features']

    # FUNCTIONS

    def minutes_of_new_data(self, symbol, kline_size, data, source):
        if len(data) > 0:
            old = parser.parse(
                data["timestamp"].iloc[-1]
            )
        elif source == "bitmex":
            old = self.bitmex_client.Trade.Trade_getBucketed(
                symbol=symbol,
                binSize=kline_size,
                count=1,
                reverse=False
            ).result()[0][0]['timestamp']
            new = self.bitmex_client.Trade.Trade_getBucketed(
                symbol=symbol,
                binSize=kline_size,
                count=1,
                reverse=True
            ).result()[0][0]['timestamp']
        return old, new

    def get_all_bitmex(self, symbol, kline_size, save=False):
        filename = f'{symbol}-{kline_size}-data.csv'

        if os.path.isfile(filename):
            data_df = pd.read_csv(filename)
        else:
            data_df = pd.DataFrame()

        if not isinstance(data_df, pd.DataFrame):
            data_df = pd.DataFrame()

        oldest_point, newest_point = self.minutes_of_new_data(
            symbol,
            kline_size,
            data_df,
            source="bitmex"
        )
        delta_min = (newest_point - oldest_point).total_seconds() / 60
        available_data = math.ceil(
            delta_min / self.BINSIZES[kline_size]
        )
        rounds = math.ceil(available_data / self.batch_size)

        if rounds > 0:
            print(
                f'Downloading {delta_min} minutes of new data available for {symbol},'
                f' i.e. {available_data} instances of {kline_size} data in {rounds} rounds.'
            )

            for round_num in tqdm(range(rounds)):
                new_time = (
                        oldest_point + timedelta(
                            minutes=round_num * self.batch_size * self.BINSIZES[kline_size]
                        )
                )
                data = self.bitmex_client.Trade.Trade_getBucketed(
                    symbol=symbol,
                    binSize=kline_size,
                    count=self.batch_size,
                    startTime=new_time
                ).result()[0]
                temp_df = pd.DataFrame(data)
                data_df = pd.concat([data_df, temp_df])

            data_df = data_df.rename(
                {'timestamp': 'Date'},
                axis=1
            )
            data = preprocess(
                data_df,
                self.cfg
            )
            return data

    def create_dataset(self, df, window_size):
        dates = df['Date']
        df = df.drop(
            'Date',
            axis=1
        )
        arr = np.array(df)
        data, profit_calculator = create_dataset(
            arr,
            list(dates),
            look_back=window_size,
            features=self.features
        )
        return data, profit_calculator

    def get_dataset(self):
        dataset = self.get_all_bitmex(
            self.symbol,
            self.bin,
            save=True
        )
        return dataset




if __name__ == '__main__':
    # Create a configuration object. This should be replaced with your actual configuration.
    cfg = {
        'dataset_loader': {
            'batch_size': 100,  # replace with your actual batch size
            'symbol': 'XBTUSD',  # replace with your actual symbol
            'binsize': '1d',  # replace with your actual binsize
            'window_size': 60,  # replace with your actual window size
            'features': ['open', 'high', 'low', 'close', 'volume'],  # replace with your actual features
            'train_start_date': '2020-01-01',  # replace with your actual train start date
            'valid_end_date': '2021-12-31',  # replace with your actual train end date
        }
    }

    # Create an instance of BitmexDataset
    bitmex_dataset = BitmexDataset(cfg)

    # Call the get_dataset method
    dataset = bitmex_dataset.get_dataset()

    # Now you can use the dataset for further processing
    print(dataset)
