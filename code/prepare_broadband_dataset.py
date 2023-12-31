import pandas as pd
from tqdm import tqdm
from merge_datasets import merge_datasets
from avg_up_using_devices import avg_up_using_devices
from avg_down_using_devices import avg_down_using_devices
from devices import devices
from perc_income_min_price_25 import perc_income_min_price_25
from perc_income_min_price_100 import perc_income_min_price_100
from perc_income_avg_nat_package import perc_income_avg_nat_package
from perc_hh_without_compdev import perc_hh_without_compdev
from perc_hh_with_broadband import perc_hh_with_broadband
from perc_hh_without_internet import perc_hh_without_internet
from perc_hh_with_cable_fiber_dsl import perc_hh_with_cable_fiber_dsl
from perc_w_int_25_3_using_devices import perc_w_int_25_3_using_devices
from perc_w_int_100_20_using_devices import perc_w_int_100_20_using_devices
from perc_total_25_3_using_devices import perc_total_25_3_using_devices
from perc_total_100_20_using_devices import perc_total_100_20_using_devices

if __name__ == "__main__":
    avg_up_using_devices()
    avg_down_using_devices()
    devices()
    perc_income_min_price_25()
    perc_income_min_price_100()
    perc_income_avg_nat_package()
    perc_hh_without_compdev()
    perc_hh_with_broadband()
    perc_hh_without_internet()
    perc_hh_with_cable_fiber_dsl()
    perc_w_int_25_3_using_devices()
    perc_w_int_100_20_using_devices()
    perc_total_25_3_using_devices()
    perc_total_100_20_using_devices()
