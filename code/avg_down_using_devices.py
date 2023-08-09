import pandas as pd
from tqdm import tqdm
import pathlib
import settings
import os


def generate_higher_geo(df, geoid_length=11):
    region_type = settings.FIPS_LENGTH_DESIGNATION[geoid_length]
    df[region_type] = df["geoid"].str[:geoid_length]
    avg_u_sum = (
        df.groupby([region_type, "year"])["download_speed"]
        .agg("sum")
        .to_frame()
        .reset_index()
    )
    devices_sum = (
        df.groupby([region_type, "year"])["devices"].agg("sum").to_frame().reset_index()
    )
    cdf = pd.merge(avg_u_sum, devices_sum, on=[region_type, "year"])
    cdf["measure"] = "avg_down_using_devices"
    cdf["value"] = cdf["download_speed"] / cdf["devices"]

    # rename the census tract back into geoid to concat
    cdf = cdf.rename(columns={region_type: "geoid"})
    cdf = cdf.reindex(settings.STANDARD_COLS, axis="columns")
    cdf["region_type"] = region_type
    return cdf


def avg_down_using_devices():
    export_dir = "../data/Accessibility/Average Download Speed/data/distribution"
    files = sorted(pathlib.Path(settings.OOKLA_DATA_DIR).glob("*.csv.xz"))
    pbar = tqdm(files)
    for file in pbar:
        df = pd.read_csv(file, dtype={"GEOID20": object})
        # Filter out empty and invalid rows
        df = df[(df["avg_d_mbps"] >= 0) & (df["avg_d_mbps"].notnull())].copy()
        df = df.rename(columns={"GEOID20": "geoid"})

        # Pre-calculate the upload speed before other operations
        df["download_speed"] = df["avg_d_mbps"] * df["devices"]

        # Generate summaries at the block group level. Since the rows should only be unique by (geoid and year) and there are multiple entries for the same geoid, year, we group and sum the values before divided
        avg_u_sum = (
            df.groupby(["geoid", "year"])["download_speed"]
            .agg("sum")
            .to_frame()
            .reset_index()
        )
        devices_sum = (
            df.groupby(["geoid", "year"])["devices"].agg("sum").to_frame().reset_index()
        )
        b_df = pd.merge(avg_u_sum, devices_sum, on=["geoid", "year"])
        b_df["measure"] = "avg_down_using_devices"
        b_df["value"] = b_df["download_speed"] / b_df["devices"]
        b_df = b_df.reindex(settings.STANDARD_COLS, axis="columns")
        b_df["region_type"] = "block"

        # Generating summaries at a census tract level
        bg_df = generate_higher_geo(df, 12)
        ct_df = generate_higher_geo(df, 11)
        c_df = generate_higher_geo(df, 5)

        fdf = pd.concat([c_df, ct_df, bg_df])

        export_filepath = os.path.join(export_dir, file.name)
        pbar.set_description("Exporting to: %s" % export_filepath)
        assert not any(fdf["geoid"].isnull())  # Sanity check
        fdf.to_csv(export_filepath, index=False)


if __name__ == "__main__":
    avg_down_using_devices()
