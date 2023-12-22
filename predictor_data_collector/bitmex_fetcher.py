import hydra
from omegaconf import DictConfig
from bitmex_dataset import BitmexDataset  # Import your BitmexDataset class
import os

os.environ['HYDRA_FULL_ERROR'] = '1'


@hydra.main(
    config_path="../configs/predictor_data_collector", config_name="bitmex_config", version_base="1.1"
)
def bitmex_fetcher(cfg: DictConfig):
    # Create an instance of BitmexDataset with Hydra configurations
    bitmex_dataset = BitmexDataset(cfg)

    # Call the get_dataset method
    dataset = bitmex_dataset.get_dataset()

    # Now you can use the dataset for further processing
    print(dataset)


if __name__ == '__main__':
    bitmex_fetcher()