import pandas as pd
import pathlib
import os
import requests
from tqdm import tqdm
from merge_datasets import merge_datasets
from avg_up_using_devices import avg_up_using_devices
from avg_down_using_devices import avg_down_using_devices
from devices import devices
from perc_income_min_price_25 import perc_income_min_price_25
from perc_income_min_price_100 import perc_income_min_price_100
from perc_income_avg_nat_package import perc_income_avg_nat_package

if __name__ == "__main__":
    avg_up_using_devices()
    avg_down_using_devices()
    devices()
    perc_income_min_price_25()
    perc_income_min_price_100()
    perc_income_avg_nat_package()
