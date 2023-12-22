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
    """
        A class used to represent a Bitmex Dataset

        ...

        Attributes
        ----------
        BINSIZES :
            dict: a dictionary mapping bin sizes to their corresponding minutes
        cfg :
            DictConfig: the configuration for the Bitmex dataset
        api_key :
            str: the API key for Bitmex
        api_secret :
            str: the API secret for Bitmex
        bitmex_client :
            str: the Bitmex client
        batch_size :
            int: the batch size for the Bitmex dataset
        symbol :
            str: the symbol for the Bitmex dataset
        bin :
            int: the bin size for the Bitmex dataset
        window_size :
            int: the window size for the Bitmex dataset
        features :
            list: the features for the Bitmex dataset
    """
    BINSIZES = {
        "1m": 1,
        "5m": 5,
        "1h": 60,
        "1d": 1440
    }

    def __init__(self, cfg: DictConfig):
        """
            Constructs all the necessary attributes for the BitmexDataset object.

            :param cfg: DictConfig: The configuration for the Bitmex dataset
        """
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
        """
            Calculate the minutes of new data for a given symbol and kline size.

            :param symbol: The symbol to calculate the minutes of new data for.
            :param kline_size: The kline size to calculate the minutes of new data for.
            :param data: The existing data for the symbol.
            :param source: The source of the data.
            :return: The oldest and newest data points.
        """
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
        """
            Fetch all Bitmex data for a given symbol and kline size.

            :param symbol: The symbol to fetch the data for.
            :param kline_size: The kline size to fetch the data for.
            :param save: Whether to save the fetched data to a file.
            :return: The fetched data.
        """
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
        """
            Create a dataset with a given dataframe and window size.

            :param df: The dataframe to create the dataset from.
            :param window_size: The window size for the dataset.
            :return: The created dataset and profit calculator.
        """
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
        """
            Fetch the dataset.

            :return: The fetched dataset.
        """
        dataset = self.get_all_bitmex(
            self.symbol,
            self.bin,
            save=True
        )
        return dataset
