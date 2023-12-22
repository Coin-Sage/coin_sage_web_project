import os
import pandas as pd
import math
import os.path
from bitmex import bitmex
from datetime import timedelta
from dateutil import parser
from tqdm import tqdm   # (Optional, used for progress-bars)
from creator import preprocess, create_dataset
import numpy as np
from omegaconf import DictConfig


class BitmexDataset:
    BINSIZES = {
        "1m": 1,
        "5m": 5,
        "1h": 60,
        "1d": 1440
    }

    def __init__(self, cfg: DictConfig):
        self.cfg = cfg
        self.api_key = os.getenv('BITMEX_API_KEY')
        self.api_secret = os.getenv('BITMEX_API_SECRET')
        self.bitmex_client = bitmex(
            test=False,
            api_key=self.api_key,
            api_secret=self.api_secret
        )
        self.batch_size = cfg.batch_size
        self.symbol = cfg.symbol
        self.bin = cfg.binsize
        self.window_size = cfg.window_size
        self.features = cfg.features
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
