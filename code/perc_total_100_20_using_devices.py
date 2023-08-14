import pandas as pd
from tqdm import tqdm
import pathlib
import settings
import os


MEASURE_NAME = "perc_total_100_20_using_devices"


def generate_higher_geo(df, geoid_length=11):
    """
    Instead of having each geography weight the same, we instead calculate the population-weighted probabilities for higher regions
    """

    region_type = settings.FIPS_LENGTH_DESIGNATION[geoid_length]
    df[region_type] = df["geoid"].str[:geoid_length]

    dfs = []
    for rt in df[region_type].unique():
        pdf = df[df[region_type] == rt].copy()
        pdf["weighted_pop"] = (pdf["B28002_001E"]) / (pdf["B28002_001E"].sum())
        pdf["value"] = (
            (pdf["upload_prob"] * pdf["download_prob"]) * pdf["weighted_pop"] * 100
        )
        assert pdf["weighted_pop"].sum() - 1 <= 0.000001, print(
            pdf["weighted_pop"].sum()
        )  # the weights should sum to one
        dfs.append(pdf)
    df = pd.concat(dfs)

    cdf = df.groupby([region_type, "year"])["value"].agg("sum").to_frame().reset_index()
    cdf["measure"] = MEASURE_NAME
    # rename the census tract back into geoid to concat
    cdf = cdf.rename(columns={region_type: "geoid"})
    cdf = cdf.reindex(settings.STANDARD_COLS, axis="columns")
    cdf["region_type"] = region_type
    return cdf


def calculate_cpdf(df, value_col="value", cutoff=25, tail=True):
    # Frequency
    stats_df = (
        df.groupby(value_col)[value_col]
        .agg("count")
        .pipe(pd.DataFrame)
        .rename(columns={value_col: "frequency"})
    )

    if stats_df.empty:
        return None

    # PDF
    stats_df["pdf"] = stats_df["frequency"] / sum(stats_df["frequency"])

    # CDF
    stats_df["cdf"] = stats_df["pdf"].cumsum()
    stats_df = stats_df.reset_index()

    if tail:
        return 1 - stats_df[stats_df[value_col] >= cutoff].min()["cdf"]
    else:
        return stats_df[stats_df[value_col] >= cutoff].min()["cdf"]


def perc_total_100_20_using_devices():
    export_dir = "../data/Accessibility/Percent Fast (total)/data/distribution"
    ookla_files = sorted(pathlib.Path(settings.OOKLA_DATA_DIR).glob("*.csv.xz"))
    acs_1_files = sorted(
        pathlib.Path("../sdc.broadband.acs/data/distribution/B28002_001").glob(
            "*.csv.xz"
        )
    )

    overlapped_filenames = sorted(
        set([f.name for f in ookla_files]).intersection(
            set([f.name for f in acs_1_files])
        )
    )

    # Filter for only overlapping files between the data sets
    ookla_files = [f for f in ookla_files if f.name in overlapped_filenames]
    acs_1_files = [f for f in acs_1_files if f.name in overlapped_filenames]

    pbar = tqdm(total=len(ookla_files))

    for ookla_f, acs1_f in zip(ookla_files, acs_1_files):
        ookla_df = pd.read_csv(ookla_f, dtype={"GEOID20": object})
        ookla_df = ookla_df.dropna()
        ookla_df = ookla_df.rename(columns={"GEOID20": "geoid"})

        acs1_df = pd.read_csv(acs1_f, dtype={"GEOID21": object})
        acs1_df = acs1_df.rename(columns={"GEOID21": "geoid"})
        acs1_df["year"] = 2021
        a1df = (
            acs1_df.groupby(["geoid", "year"])["B28002_001E"]
            .agg("min")
            .to_frame()
            .reset_index()
        )
        a1df = a1df[a1df["B28002_001E"] > 0]
        a1df[
            "year"
        ] = 2022  # TBD should be adjusted for inflation for moving forward in time?

        bg_df = a1df
        bg_df["upload_prob"] = bg_df["geoid"].apply(
            lambda x: calculate_cpdf(
                ookla_df[ookla_df["geoid"].str[: len(x)] == x], "avg_u_mbps", 20
            )
        )
        bg_df["download_prob"] = bg_df["geoid"].apply(
            lambda x: calculate_cpdf(
                ookla_df[ookla_df["geoid"].str[: len(x)] == x], "avg_d_mbps", 100
            )
        )

        ct_df = generate_higher_geo(bg_df, 11)
        c_df = generate_higher_geo(bg_df, 5)

        bdf = bg_df.copy()
        bdf["measure"] = MEASURE_NAME
        bdf["value"] = (bdf["upload_prob"] * bdf["download_prob"]) * 100
        bdf = bdf.reindex(settings.STANDARD_COLS, axis="columns")
        bdf["region_type"] = "block_group"
        fdf = pd.concat([c_df, ct_df, bdf])
        fdf = fdf.reindex(settings.STANDARD_COLS, axis="columns")
        export_filepath = os.path.join(export_dir, acs1_f.name)
        pbar.set_description("Exporting to: %s" % export_filepath)
        assert not any(fdf["geoid"].isnull())  # Sanity check
        fdf.to_csv(export_filepath, index=False)
        pbar.update(1)


if __name__ == "__main__":
    perc_total_100_20_using_devices()
