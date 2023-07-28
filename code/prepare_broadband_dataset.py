import pandas as pd
import pathlib
import os
import requests
from tqdm import tqdm
from merge_datasets import merge_datasets

STANDARD_DATA_COLS_URL = "https://raw.githubusercontent.com/uva-bi-sdad/sdc.metadata/master/data/column_structure.json"

COUNTIES_TO_FOCUS = [
    "01073",
    "01117",
    "01007",
    "01125",
    "01043",
    "01009",
    "01115",
    "13057",
    "13117",
    "13135",
    "13247",
    "13151",
    "13113",
    "13089",
    "13121",
    "13097",
    "13067",
    "13063",
]


def perc(a, b):
    return a / b * 100


def perc_income_on_internet(export_dir):
    acs_data_dir = "../sdc.broadband.acs/data/distribution"
    bbn_data_dir = "../sdc.broadband.broadbandnow/data/distribution"
    assert os.path.isdir(bbn_data_dir) and os.path.isdir(acs_data_dir)

    def process_bbn(bbn_df):
        # Extract just minimum value for 100 mbps upload
        bbn_df["speed_val"] = bbn_df["speed"].apply(lambda x: int(x.split("Mbps")[0]))
        min_up_100 = bbn_df[
            (bbn_df["down_up"] == "Upload") & (bbn_df["speed_val"] >= 25)
        ]
        min_df = min_up_100.groupby(["GEOID20"])["price"].min()
        min_df = min_df.reset_index()
        min_df["year"] = 2023
        min_df["price"] *= 12  # change per month price to per year price to match acs
        return min_df

    def process_acs(df):
        df["year"] = 2021
        df = df[(df["B19013_001E"] >= 0) & (df["B19013_001E"].notnull())]
        return df

    merge_datasets(
        "perc_income_min_price_100",
        bbn_data_dir,
        acs_data_dir,
        "GEOID20",
        "GEOID21",
        "price",
        "B19013_001E",
        process_bbn,
        process_acs,
        perc,
        "year",
        "year",
        export_dir,
        glob="*.csv.xz",
        save=True,
    )


def perc_income_min_price_100(export_dir):
    acs_data_dir = "../sdc.broadband.acs/data/distribution"
    bbn_data_dir = "../sdc.broadband.broadbandnow/data/distribution"
    assert os.path.isdir(bbn_data_dir) and os.path.isdir(acs_data_dir)

    def process_bbn(bbn_df):
        # Extract just minimum value for 100 mbps upload
        bbn_df["speed_val"] = bbn_df["speed"].apply(lambda x: int(x.split("Mbps")[0]))
        min_up_100 = bbn_df[
            (bbn_df["down_up"] == "Upload") & (bbn_df["speed_val"] >= 100)
        ]
        min_df = min_up_100.groupby(["GEOID20"])["price"].min()
        min_df = min_df.reset_index()
        min_df["year"] = 2023
        min_df["price"] *= 12  # change per month price to per year price to match acs
        return min_df

    def process_acs(df):
        df["year"] = 2021
        df = df[(df["B19013_001E"] >= 0) & (df["B19013_001E"].notnull())]
        return df

    merge_datasets(
        "perc_income_min_price_100",
        bbn_data_dir,
        acs_data_dir,
        "GEOID20",
        "GEOID21",
        "price",
        "B19013_001E",
        process_bbn,
        process_acs,
        perc,
        "year",
        "year",
        export_dir,
        glob="*.csv.xz",
        save=True,
    )


def perc_income_avg_nat_package(export_dir):
    acs_data_dir = "../sdc.broadband.acs/data/distribution"
    assert os.path.isdir(acs_data_dir)
    standard_cols = requests.get(STANDARD_DATA_COLS_URL).json()

    def process_acs(df, measure_name, standard_cols):
        df["year"] = 2021
        df = df[(df["B19013_001E"] >= 0) & (df["B19013_001E"].notnull())].copy()
        df = df.rename(columns={"GEOID21": "geoid"})
        df["value"] = 64 / df["B19013_001E"]
        df = df.reindex(standard_cols, axis="columns")
        df["measure"] = measure_name
        return df

    pbar = tqdm(sorted(pathlib.Path(acs_data_dir).glob("*.csv.xz")))
    for file in pbar:
        if not file.name[:5] in COUNTIES_TO_FOCUS:
            continue
        df = process_acs(
            pd.read_csv(file, dtype={"GEOID21": object}),
            "perc_income_avg_nat_package",
            standard_cols,
        )
        export_filepath = os.path.join(export_dir, file.name)
        pbar.set_description("Saving file to: %s" % export_filepath)
        assert not any(df["geoid"].isnull())
        df.to_csv(export_filepath, index=False)


def avg_down_using_devices(export_dir):
    ookla_data_dir = "../sdc.broadband.ookla/data/distribution"
    assert os.path.isdir(ookla_data_dir)
    standard_cols = requests.get(STANDARD_DATA_COLS_URL).json()

    def process_ookla(df, measure_name, standard_cols):
        df = df[(df["avg_d_mbps"] >= 0) & (df["avg_d_mbps"].notnull())].copy()
        df = df.rename(columns={"GEOID20": "geoid", "avg_d_mbps": "value"})
        df = df.reindex(standard_cols, axis="columns")
        df["measure"] = measure_name
        return df

    pbar = tqdm(sorted(pathlib.Path(ookla_data_dir).glob("*.csv.xz")))
    for file in pbar:
        if not file.name[:5] in COUNTIES_TO_FOCUS:
            continue
        df = process_ookla(
            pd.read_csv(file, dtype={"GEOID20": object}),
            "avg_down_using_devices",
            standard_cols,
        )
        export_filepath = os.path.join(export_dir, file.name)
        pbar.set_description("Saving file to: %s" % export_filepath)
        assert not any(df["geoid"].isnull())
        df.to_csv(export_filepath, index=False)


if __name__ == "__main__":
    perc_income_min_price_100(
        "../data/distribution/Affordability/Percentage of income for fast internet/"
    )
    perc_income_on_internet(
        "../data/distribution/Affordability/Percentage of income for good internet/"
    )
    perc_income_avg_nat_package(
        "../data/distribution/Affordability/Percentage of income for internet (average)/"
    )
    avg_down_using_devices("../data/distribution/Accessibility/Average Download Speed/")
