import pandas as pd
import pathlib
import os
import requests
from tqdm import tqdm


MERGED_GEOID_COL_NAME = "geoid"
MERGED_YEAR_COL_NAME = "year"
MERGED_VAL_COL_NAME = "value"


"""
Assumptions:
    - Using a unix system
    - Has access to the internet and GitHub is not down
"""


def perc(a, b):
    return a / b * 100


def merge_data(
    measure_name,
    a_df,
    b_df,
    geoid_col_a,
    geoid_col_b,
    measure_col_a,
    measure_col_b,
    operation,
    year_col_a,
    year_col_b,
):
    standard_cols = requests.get(
        "https://raw.githubusercontent.com/uva-bi-sdad/sdc.metadata/master/data/column_structure.json"
    ).json()

    # Rename the names of the columns to a standardized one before merging on it
    a_df = a_df.rename(columns={geoid_col_a: MERGED_GEOID_COL_NAME})
    b_df = b_df.rename(columns={geoid_col_b: MERGED_GEOID_COL_NAME})
    mdf = pd.merge(a_df, b_df, how="inner", on=MERGED_GEOID_COL_NAME)

    # Drops data where anything is missing
    mdf = mdf[(mdf[measure_col_a].notnull()) & (mdf[measure_col_b].notnull())]
    mdf[MERGED_VAL_COL_NAME] = operation(mdf[measure_col_a], mdf[measure_col_b])

    # Right now, decisions about the year is being decided by the freshness of the most recently merged data
    # print(mdf)
    mdf[MERGED_YEAR_COL_NAME] = mdf[[year_col_a + "_x", year_col_b + "_y"]].max(axis=1)

    # Convert the data to a standard format
    mdf = mdf.reindex(standard_cols, axis="columns")
    mdf["measure"] = measure_name
    return mdf


def merge_datasets(
    measure_name,
    dir_a,
    dir_b,
    geoid_col_a,
    geoid_col_b,
    measure_col_a,
    measure_col_b,
    process_a,
    process_b,
    operation,
    year_col_a,
    year_col_b,
    export_dir,
    glob="*.csv.xz",
    save=False,
):
    assert os.path.isdir(dir_a) and os.path.isdir(dir_b)

    # Grab all the files
    a_files = set([v.name for v in list(pathlib.Path(dir_a).glob(glob))])
    b_files = set([v.name for v in list(pathlib.Path(dir_b).glob(glob))])

    # For each intersecting file name
    pbar = tqdm(sorted(a_files.intersection(b_files)))
    for file in pbar:
        a_df = process_a(
            pd.read_csv(os.path.join(dir_a, file), dtype={geoid_col_a: object})
        )
        b_df = process_b(
            pd.read_csv(os.path.join(dir_b, file), dtype={geoid_col_b: object})
        )

        # Check that all of the columns are in order
        assert set([measure_col_a, year_col_a, geoid_col_a]).issubset(
            set(a_df.columns)
        ), print("%s / %s" % ([measure_col_a, year_col_a, geoid_col_a], a_df.columns))
        assert set([measure_col_b, year_col_b, geoid_col_b]).issubset(
            set(b_df.columns)
        ), print(b_df.columns)

        mdf = merge_data(
            measure_name,
            a_df,
            b_df,
            geoid_col_a,
            geoid_col_b,
            measure_col_a,
            measure_col_b,
            operation,
            year_col_a,
            year_col_b,
        )

        export_filepath = os.path.join(export_dir, file)

        if save:
            os.system("mkdir -p %s" % export_dir)
            pbar.set_description("Saving file to: %s" % export_filepath)
            mdf.to_csv(export_filepath, index=False)
        else:
            print(mdf)


if __name__ == "__main__":
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
        "../data/distribution/",
        glob="*.csv.xz",
        save=True,
    )
