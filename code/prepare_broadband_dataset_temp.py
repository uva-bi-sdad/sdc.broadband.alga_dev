import pandas as pd
import pathlib
import os
import requests
from tqdm import tqdm
from merge_datasets import merge_datasets

STANDARD_COLS = requests.get(
    "https://raw.githubusercontent.com/uva-bi-sdad/sdc.metadata/master/data/column_structure.json"
).json()

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

    def process_acs(df, measure_name):
        df["year"] = 2021
        df = df[(df["B19013_001E"] >= 0) & (df["B19013_001E"].notnull())].copy()
        df = df.rename(columns={"GEOID21": "geoid"})
        df["value"] = 64 / df["B19013_001E"]
        df = df.reindex(STANDARD_COLS, axis="columns")
        df["measure"] = measure_name
        return df

    pbar = tqdm(sorted(pathlib.Path(acs_data_dir).glob("*.csv.xz")))
    for file in pbar:
        if not file.name[:5] in COUNTIES_TO_FOCUS:
            continue
        df = process_acs(
            pd.read_csv(file, dtype={"GEOID21": object}),
            "perc_income_avg_nat_package",
        )
        export_filepath = os.path.join(export_dir, file.name)
        pbar.set_description("Saving file to: %s" % export_filepath)
        assert not any(df["geoid"].isnull())
        df.to_csv(export_filepath, index=False)


def avg_down_using_devices(export_dir):
    ookla_data_dir = "../sdc.broadband.ookla/data/distribution"
    assert os.path.isdir(ookla_data_dir)

    def process_ookla(df, measure_name):
        df = df[(df["avg_d_mbps"] >= 0) & (df["avg_d_mbps"].notnull())].copy()
        df = df.rename(columns={"GEOID20": "geoid", "avg_d_mbps": "value"})
        df = df.groupby(["geoid", "year"])["value"].agg("mean").reset_index()
        df["moe"] = None
        df = df.reindex(STANDARD_COLS, axis="columns")
        df["measure"] = measure_name
        return df

    files = sorted(pathlib.Path(ookla_data_dir).glob("*.csv.xz"))
    files = [f for f in files if f.name[:5] in COUNTIES_TO_FOCUS]

    pbar = tqdm(files)
    for file in pbar:
        df = process_ookla(
            pd.read_csv(file, dtype={"GEOID20": object}),
            "avg_down_using_devices",
        )
        export_filepath = os.path.join(export_dir, file.name)
        pbar.set_description("Saving file to: %s" % export_filepath)
        assert not any(df["geoid"].isnull())
        df.to_csv(export_filepath, index=False)


def avg_up_using_devices(export_dir):
    ookla_data_dir = "../sdc.broadband.ookla/data/distribution"
    assert os.path.isdir(ookla_data_dir)

    def process_ookla(df, measure_name):
        df = df[(df["avg_u_mbps"] >= 0) & (df["avg_u_mbps"].notnull())].copy()
        df = df.rename(columns={"GEOID20": "geoid", "avg_u_mbps": "value"})
        df = df.groupby(["geoid", "year"])["value"].agg("mean").reset_index()
        df["moe"] = None
        df = df.reindex(STANDARD_COLS, axis="columns")
        df["measure"] = measure_name
        return df

    files = sorted(pathlib.Path(ookla_data_dir).glob("*.csv.xz"))
    files = [f for f in files if f.name[:5] in COUNTIES_TO_FOCUS]
    pbar = tqdm(files)
    for file in pbar:
        df = process_ookla(
            pd.read_csv(file, dtype={"GEOID20": object}),
            "avg_up_using_devices",  # ! The function name is also the measure name
        )
        export_filepath = os.path.join(export_dir, file.name)
        pbar.set_description("Saving file to: %s" % export_filepath)
        assert not any(df["geoid"].isnull())
        df.to_csv(export_filepath, index=False)


def devices(export_dir):
    ookla_data_dir = "../sdc.broadband.ookla/data/distribution"
    assert os.path.isdir(ookla_data_dir)

    def process_ookla(df, measure_name):
        df = df[(df["devices"] >= 0) & (df["devices"].notnull())].copy()
        df = df.rename(columns={"GEOID20": "geoid", "devices": "value"})
        df = df.groupby(["geoid", "year"])["value"].agg("mean").reset_index()
        df["moe"] = None
        df = df.reindex(STANDARD_COLS, axis="columns")
        df["measure"] = measure_name
        return df

    files = sorted(pathlib.Path(ookla_data_dir).glob("*.csv.xz"))
    files = [f for f in files if f.name[:5] in COUNTIES_TO_FOCUS]
    pbar = tqdm(files)
    for file in pbar:
        df = process_ookla(
            pd.read_csv(file, dtype={"GEOID20": object}),
            "devices",  # ! The function name is also the measure name
        )
        export_filepath = os.path.join(export_dir, file.name)
        pbar.set_description("Saving file to: %s" % export_filepath)
        assert not any(df["geoid"].isnull())
        df.to_csv(export_filepath, index=False)


def perc_hh_with_broadband(export_dir):
    """
    has_broadband_hhE/total_intsub_hhE * 100
    B28002_004 / B28002_001 * 100
    """
    has_broadband_hh_dir = "../sdc.broadband.acs/data/distribution/B28002_004"
    total_intsub_hhE = "../sdc.broadband.acs/data/distribution/B28002_001"
    assert os.path.isdir(has_broadband_hh_dir)
    assert os.path.isdir(total_intsub_hhE)

    def process_acs(df, col_name, measure_name):
        df["year"] = 2021
        df = df[(df[col_name] >= 0) & (df[col_name].notnull())].copy()
        df = df.rename(columns={"GEOID21": "geoid"})
        df["value"] = df[col_name]
        df = df.reindex(STANDARD_COLS, axis="columns")
        df["measure"] = measure_name
        return df

    overlapped = set(pathlib.Path(has_broadband_hh_dir).glob("*.csv.xz")).intersection(
        [v.name for v in pathlib.Path(total_intsub_hhE).glob("*.csv.xz")])
    )
    print(set(pathlib.Path(total_intsub_hhE).glob("*.csv.xz")))
    print("Overlapped: %s" % overlapped)

    pbar = tqdm(overlapped)

    for file in pbar:
        if not file.name[:5] in COUNTIES_TO_FOCUS:
            continue
        df1 = process_acs(
            pd.read_csv(file, dtype={"GEOID21": object}),
            "has_broadband_hh",
        )
        df2 = process_acs(
            pd.read_csv(file, dtype={"GEOID21": object}),
            "total_intsub_hhE",
        )

        # list(set(item_list) - set(list_to_remove))
        fdf = pd.merge(
            on=list(set(STANDARD_COLS) - set(["measure", "value"])), how="inner"
        )
        print(fdf)
        input("test")
        fdf["measure"] = "perc_hh_with_broadband"
        fdf["value"] = fdf["value_x"] / fdf["value_y"] * 100
        fdf = fdf.reindex(STANDARD_COLS, axis="columns")
        export_filepath = os.path.join(export_dir, file.name)
        pbar.set_description("Saving file to: %s" % export_filepath)
        assert not any(fdf["geoid"].isnull())
        # fdf.to_csv(export_filepath, index=False)


if __name__ == "__main__":
    # perc_income_min_price_100(
    #     "../data/distribution/Affordability/Percentage of income for fast internet/"
    # )
    # perc_income_on_internet(
    #     "../data/distribution/Affordability/Percentage of income for good internet/"
    # )
    # perc_income_avg_nat_package(
    #     "../data/distribution/Affordability/Percentage of income for internet (average)/"
    # )
    # avg_down_using_devices("../data/distribution/Accessibility/Average Download Speed/")
    # avg_up_using_devices("../data/distribution/Accessibility/Average Upload Speed/")
    # devices("../data/distribution/Accessibility/Number of Devices/")
    perc_hh_with_broadband(
        "../data/distribution/Affordability/Households with broadband/"
    )
