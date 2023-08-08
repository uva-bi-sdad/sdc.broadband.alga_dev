import pandas as pd
import pathlib
import os
import requests
from tqdm import tqdm
from merge_datasets import merge_datasets
from avg_up_using_devices import avg_up_using_devices
from avg_down_using_devices import avg_down_using_devices

if __name__ == "__main__":
    avg_up_using_devices()
    avg_down_using_devices()
