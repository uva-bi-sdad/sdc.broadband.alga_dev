import os
import requests

# Linking data sources
OOKLA_DATA_DIR = "../sdc.broadband.ookla/data/distribution"
ACS_DATA_DIR = "../sdc.broadband.acs/data/distribution"
BBN_DATA_DIR = "../sdc.broadband.broadbandnow/data/distribution"

assert (
    os.path.isdir(OOKLA_DATA_DIR)
    and os.path.isdir(ACS_DATA_DIR)
    and os.path.isdir(BBN_DATA_DIR)
)

# Column standards for exports
STANDARD_COLS = requests.get(
    "https://raw.githubusercontent.com/uva-bi-sdad/sdc.metadata/master/data/column_structure.json"
).json()

# Counties to keep track of
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

FIPS_LENGTH_DESIGNATION = {5: "county", 11: "tract", 12: "block group"}
