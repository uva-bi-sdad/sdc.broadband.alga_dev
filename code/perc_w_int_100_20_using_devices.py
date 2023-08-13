import pandas as pd
from tqdm import tqdm
import pathlib
import settings
import os
import scipy

MEASURE_NAME = "perc_w_int_100_20_using_devices"


def generate_higher_geo(df, geoid_length=11):
    region_type = settings.FIPS_LENGTH_DESIGNATION[geoid_length]
    df[region_type] = df["geoid"].str[:geoid_length]
    cdf = (
        df.groupby([region_type, "year"])["value"].agg("mean").to_frame().reset_index()
    )
    cdf["measure"] = MEASURE_NAME
    # rename the census tract back into geoid to concat
    cdf = cdf.rename(columns={region_type: "geoid"})
    cdf = cdf.reindex(settings.STANDARD_COLS, axis="columns")
    cdf["region_type"] = region_type
    return cdf


def perc_w_int_100_20_using_devices():
    export_dir = (
        "../data/Accessibility/Percent Fast (internet-connected)/data/distribution"
    )
    bbn_files = sorted(pathlib.Path(settings.BBN_DATA_DIR).glob("*.csv.xz"))
    acs_1_files = sorted(
        pathlib.Path("../sdc.broadband.acs/data/distribution/B28002_001").glob(
            "*.csv.xz"
        )
    )
    acs_13_files = sorted(
        pathlib.Path("../sdc.broadband.acs/data/distribution/B28002_013").glob(
            "*.csv.xz"
        )
    )

    overlapped_filenames = sorted(
        set([f.name for f in bbn_files]).intersection(
            set([f.name for f in acs_1_files]).intersection(
                set([f.name for f in acs_13_files])
            )
        )
    )

    # Filter for only overlapping files between the data sets
    bbn_files = [f for f in bbn_files if f.name in overlapped_filenames]
    acs_1_files = [f for f in acs_1_files if f.name in overlapped_filenames]
    acs_13_files = [f for f in acs_13_files if f.name in overlapped_filenames]

    pbar = tqdm(zip(bbn_files, acs_1_files, acs_13_files))
    for bbn_f, acs1_f, acs_13_f in pbar:
        bbn_df = pd.read_csv(bbn_f, dtype={"GEOID20": object})
        # Preparing bbn file; remove all not nulls but also the specific none-standard values
        bbn_df = bbn_df[(bbn_df["price"] >= 0) & (bbn_df["price"].notnull())].copy()
        bbn_df = bbn_df.rename(columns={"GEOID20": "geoid"})
        bbn_df["speed_value"] = bbn_df["speed"].apply(
            lambda x: int(x.split(" Mbps")[0])
        )
        bbn_df_d_100 = bbn_df[
            (bbn_df["down_up"] == "Download") & (bbn_df["speed_value"] >= 100)
        ]
        bbn_df_u_20 = bbn_df[
            (bbn_df["down_up"] == "Upload") & (bbn_df["speed_value"] >= 20)
        ]
        bdf = pd.merge(bbn_df_d_100, bbn_df_u_20, on=["name", "geoid"], how="inner")

        bdf = (
            bdf.groupby(["geoid", "year_parsed"])["price"]
            .agg("min")
            .to_frame()
            .reset_index()
        )
        bdf = bdf.rename(columns={"year_parsed": "year"})

        acs_df = pd.read_csv(acs_f, dtype={"GEOID21": object})
        acs_df = acs_df.rename(columns={"GEOID21": "geoid"})
        acs_df["year"] = 2021
        adf = (
            acs_df.groupby(["geoid", "year"])["B19013_001E"]
            .agg("min")
            .to_frame()
            .reset_index()
        )
        adf = adf[adf["B19013_001E"] > 0]
        adf[
            "year"
        ] = 2023  # TBD should be adjusted for inflation for moving forward in time?

        bg_df = pd.merge(adf, bdf, on=["geoid", "year"])
        bg_df["measure"] = MEASURE_NAME
        bg_df["value"] = (
            (bg_df["price"] * 12) / bg_df["B19013_001E"] * 100
        )  # Multiplpy by 12 because it is price per month
        bg_df = bg_df.reindex(settings.STANDARD_COLS, axis="columns")
        bg_df["region_type"] = "block_group"

        # Generating summaries at a census tract level
        ct_df = generate_higher_geo(bg_df, 11)
        c_df = generate_higher_geo(bg_df, 5)

        fdf = pd.concat([c_df, ct_df, bg_df])
        fdf = fdf.reindex(settings.STANDARD_COLS, axis="columns")
        export_filepath = os.path.join(export_dir, acs_f.name)
        pbar.set_description("Exporting to: %s" % export_filepath)
        assert not any(fdf["geoid"].isnull())  # Sanity check
        fdf.to_csv(export_filepath, index=False)


if __name__ == "__main__":
    perc_w_int_100_20_using_devices()
