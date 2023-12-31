import pandas as pd
from tqdm import tqdm
import pathlib
import settings
import os

MEASURE_NAME = "devices"


def generate_higher_geo(df, geoid_length=11):
    region_type = settings.FIPS_LENGTH_DESIGNATION[geoid_length]
    df[region_type] = df["geoid"].str[:geoid_length]
    devices_sum = (
        df.groupby([region_type, "year"])[MEASURE_NAME]
        .agg("sum")
        .to_frame()
        .reset_index()
    )
    cdf = devices_sum
    cdf["measure"] = MEASURE_NAME
    cdf["value"] = cdf[MEASURE_NAME]

    # rename the census tract back into geoid to concat
    cdf = cdf.rename(columns={region_type: "geoid"})
    cdf = cdf.reindex(settings.STANDARD_COLS, axis="columns")
    cdf["region_type"] = region_type
    return cdf


def devices():
    export_dir = "../data/Accessibility/Number of Devices/data/distribution"
    files = sorted(pathlib.Path(settings.OOKLA_DATA_DIR).glob("*.csv.xz"))
    pbar = tqdm(files)
    for file in pbar:
        # Skip non-related counties
        if not file.name[:5] in settings.COUNTIES_TO_FOCUS:
            continue
        df = pd.read_csv(file, dtype={"GEOID20": object})
        # Filter out empty and invalid rows
        df = df[(df[MEASURE_NAME] >= 0) & (df[MEASURE_NAME].notnull())].copy()
        df = df.rename(columns={"GEOID20": "geoid"})

        # Generate summaries at the block group level. Since the rows should only be unique by (geoid and year) and there are multiple entries for the same geoid, year, we group and sum the values before divided
        devices_sum = (
            df.groupby(["geoid", "year"])[MEASURE_NAME]
            .agg("sum")
            .to_frame()
            .reset_index()
        )
        bdf = devices_sum
        bdf["measure"] = MEASURE_NAME
        bdf["value"] = bdf[MEASURE_NAME]
        bdf = bdf.reindex(settings.STANDARD_COLS, axis="columns")
        bdf["region_type"] = "block"

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
    devices()
