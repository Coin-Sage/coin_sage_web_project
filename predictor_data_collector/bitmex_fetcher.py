import hydra
from django.core.management import call_command
from omegaconf import DictConfig
from bitmex_dataset import BitmexDataset  # Import your BitmexDataset class
import os
import django
import yaml
import sys

# Get the absolute path to the config file
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, '../configs/predictor_data_collector/bitmex_config.yaml')

# Add the project directory to the sys.path
project_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
django_project_directory = os.path.join(project_directory, 'coin_sage_web_project')
sys.path.append(project_directory)
sys.path.append(django_project_directory)

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coin_sage_web_project.settings')
# Initialize Django
django.setup()

os.environ['HYDRA_FULL_ERROR'] = '1'


@hydra.main(
    config_path="../configs/predictor_data_collector", config_name="bitmex_config", version_base="1.1"
)
def bitmex_fetcher(cfg: DictConfig):
    # Import create_model function after Django setup
    from historical_data.models import create_model

    # Create an instance of BitmexDataset with Hydra configurations
    bitmex_dataset = BitmexDataset(cfg)

    # Call the get_dataset method
    dataset = bitmex_dataset.get_dataset()

    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    symbol = config['symbol']

    model = create_model(symbol)

    call_command('makemigrations', 'historical_data')
    call_command('migrate', 'historical_data')

    # for data_point in dataset:
    #     historical_data = model(
    #         date=data_point.get('date'),
    #         open=data_point.get('open'),
    #         high=data_point.get('high'),
    #         low=data_point.get('low'),
    #         close=data_point.get('close'),
    #         volume=data_point.get('volume'),
    #         market_cap=data_point.get('market_cap'),
    #         slug=data_point.get('slug'),
    #     )
    #     historical_data.save()
    #
    # # Now you can use the dataset for further processing
    # print(dataset)


if __name__ == '__main__':
    bitmex_fetcher()
