import pandas as pd
from tqdm import tqdm
import pathlib
import settings
import os

MEASURE_NAME = "perc_hh_with_broadband"


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


def perc_hh_with_broadband():
    export_dir = "../data/Adoption/Households with broadband/data/distribution"
    c_files = sorted(
        pathlib.Path("../sdc.broadband.acs/data/distribution/B28002_004").glob(
            "*.csv.xz"
        )
    )
    d_files = sorted(
        pathlib.Path("../sdc.broadband.acs/data/distribution/B28002_001").glob(
            "*.csv.xz"
        )
    )
    overlapped_filenames = sorted(
        set([f.name for f in c_files]).intersection(set([f.name for f in d_files]))
    )

    # Filter for only overlapping files
    c_files = [f for f in c_files if f.name in overlapped_filenames]
    d_files = [f for f in d_files if f.name in overlapped_filenames]

    pbar = tqdm(zip(c_files, d_files))
    for c_f, d_f in pbar:
        comp_df = pd.read_csv(c_f, dtype={"GEOID21": object})
        # Preparing bbn file; remove all not nulls but also the specific none-standard values
        comp_df = comp_df[
            (comp_df["B28002_004E"] >= 0) & (comp_df["B28002_004E"].notnull())
        ].copy()
        comp_df = comp_df.rename(columns={"GEOID21": "geoid"})
        comp_df["year"] = 2021
        comp_df = (
            comp_df.groupby(["geoid", "year"])["B28002_004E"]
            .agg("min")
            .to_frame()
            .reset_index()
        )

        cd_df = pd.read_csv(d_f, dtype={"GEOID21": object})
        cd_df = cd_df[
            (cd_df["B28002_001E"] >= 0) & (cd_df["B28002_001E"].notnull())
        ].copy()
        cd_df = cd_df.rename(columns={"GEOID21": "geoid"})
        cd_df["year"] = 2021
        cd_df = (
            cd_df.groupby(["geoid", "year"])["B28002_001E"]
            .agg("min")
            .to_frame()
            .reset_index()
        )
        cd_df = cd_df[cd_df["B28002_001E"] > 0]
        bg_df = pd.merge(comp_df, cd_df, on=["geoid", "year"])
        bg_df["measure"] = MEASURE_NAME
        bg_df["value"] = bg_df["B28002_004E"] / bg_df["B28002_001E"] * 100
        bg_df = bg_df.reindex(settings.STANDARD_COLS, axis="columns")
        bg_df["region_type"] = "block_group"

        # Generating summaries at a census tract level
        ct_df = generate_higher_geo(bg_df, 11)
        c_df = generate_higher_geo(bg_df, 5)

        fdf = pd.concat([c_df, ct_df, bg_df])
        fdf = fdf.reindex(settings.STANDARD_COLS, axis="columns")
        export_filepath = os.path.join(export_dir, c_f.name)
        pbar.set_description("Exporting to: %s" % export_filepath)
        assert not any(fdf["geoid"].isnull())  # Sanity check
        fdf.to_csv(export_filepath, index=False)


if __name__ == "__main__":
    perc_hh_with_broadband()
