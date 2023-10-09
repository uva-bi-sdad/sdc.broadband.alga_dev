# remotes::install_github("uva-bi-sdad/community")
library(community)

# get GEOID to entity info map
# entities_file <- "../entities.rds"
# if (file.exists(entities_file)) {
#   entities <- readRDS(entities_file)
# } else {R
#   file <- tempfile(fileext = ".csv.xz")
#   download.file(paste0(
#     "https://raw.githubusercontent.com/uva-bi-sdad/sdc.geographies/main/",
#     "docs/distribution/geographies_metadata.csv.xz"
#   ), file)
#   entities <- vroom::vroom(file)
#   entities <- entities[!duplicated(entities$geoid), c("geoid", "region_type")]
#   saveRDS(entities, entities_file, compress = "xz")
# }

entities <- read.csv("docs/data/custom_entity.csv")

# check data and measure info
check_repository(dataset = structure(entities$region_type, names = entities$geoid), exclude=c('sdc.broadband.acs', 'sdc.broadband.ookla', 'sdc.broadband.broadbandnow'))

# rebuild site
## unify original files

avg_down_using_devices <- Sys.glob("data/Accessibility/Average Download Speed/data/distribution/*.csv.xz")
avg_up_using_devices <- Sys.glob("data/Accessibility/Average Upload Speed/data/distribution/*.csv.xz")
devices <- Sys.glob("data/Accessibility/Number of Devices/data/distribution/*.csv.xz")
perc_income_min_price_25 <- Sys.glob("data/Affordability/Percentage of income for good internet/data/distribution/*.csv.xz")
perc_income_min_price_100 <- Sys.glob("data/Affordability/Percentage of income for fast internet/data/distribution/*.csv.xz")
perc_income_avg_nat_package <- Sys.glob("data/Affordability/Percentage of income for internet (average)/data/distribution/*.csv.xz")
perc_hh_without_compdev <- Sys.glob("data/Adoption/Households without a computer/data/distribution/*.csv.xz")
perc_hh_with_broadband <- Sys.glob("data/Adoption/Households with broadband/data/distribution/*.csv.xz")
perc_hh_without_internet <- Sys.glob("data/Adoption/Households without internet access/data/distribution/*.csv.xz")
perc_hh_with_cable_fiber_dsl <- Sys.glob("data/Adoption/Households with cable, fiber optic, or DSL/data/distribution/*.csv.xz")
perc_w_int_100_20_using_devices <- Sys.glob("data/Accessibility/Percent Fast (internet-connected)/data/distribution/*.csv.xz")
perc_w_int_25_3_using_devices <- Sys.glob("data/Accessibility/Percent Good (internet-connected)/data/distribution/*.csv.xz")
perc_total_100_20_using_devices <- Sys.glob("data/Accessibility/Percent Fast (total)/data/distribution/*.csv.xz")
perc_total_25_3_using_devices <- Sys.glob("data/Accessibility/Percent Good (total)/data/distribution/*.csv.xz")

datasets <- c(
  avg_down_using_devices, 
  avg_up_using_devices, 
  devices, 
  perc_income_min_price_25,
  perc_income_min_price_100,
  perc_income_avg_nat_package,
  perc_hh_without_compdev,
  perc_hh_with_broadband,
  perc_hh_without_internet,
  perc_hh_with_cable_fiber_dsl,
  perc_w_int_100_20_using_devices,
  perc_w_int_25_3_using_devices,
  perc_total_100_20_using_devices,
  perc_total_25_3_using_devices
)

data_reformat_sdad(
  datasets, "docs/data", metadata = entities,
  entity_info = NULL, overwrite=TRUE
)
info <- lapply(
  paste0('data/', list.files(path='data', pattern = "measure_info.json$", recursive = TRUE)),
  jsonlite::read_json
)
agg_info <- list()
for (m in info) {
  for (e in names(m)) {
    agg_info[[e]] <- if (e %in% names(agg_info)) c(agg_info[[e]], m[[e]]) else m[[e]]
  }
}
if (length(agg_info)) {
  jsonlite::write_json(agg_info, "docs/data/measure_info.json", auto_unbox = TRUE, pretty = TRUE)
}

## add unified files
files <- paste0("docs/data/", list.files("docs/data/", "\\.csv\\.xz$"))

### make complete maps
dir.create("docs/maps", FALSE)
map_files <- list.files("docs/maps")
if (!length(map_files)) {
  if (!require(catchment)) {
    remotes::install_github("uva-bi-sdad/catchment")
    library(catchment)
  }
  ids <- unique(unlist(lapply(files, function(f) {
    unique(vroom::vroom(f, col_select = "ID", show_col_types = FALSE)[[1]])
  })))
  states <- unique(substring(ids[
    ids %in% entities$geoid[entities$region_type %in% c("county", "tract", "block group")]
  ], 1, 2))
  states <- unique(substring(ids,1,2))
  years <- as.numeric(unique(unlist(lapply(files, function(f) {
    unique(vroom::vroom(f, col_select = "time", show_col_types = FALSE)[[1]])
  }))))
  years[years > 2022] = 2022
  for (y in years) {
    for (l in c("county", "tract", "bg")) {
      f <- paste0("docs/maps/", l, "_", y, ".geojson")
      if (!file.exists(f)) {
        ms <- do.call(rbind, lapply(states, function(s) {
          download_census_shapes(
            fips = s, entity = l, name = paste0(l, y, s), year = y
          )[, "GEOID", drop = FALSE]
        }))
        sf::st_write(ms, f)
      }
    }
  }
}

data_add(
  structure(files, names = gsub("^docs/data/|\\.csv\\.xz$", "", files)),
  meta = list(
    ids = list(variable = "ID"),
    time = "time",
    variables = "docs/data/measure_info.json"
  ),
  dir = "docs/data"
)

site_build("../sdc.broadband.alga_dev", serve = TRUE, open_after = TRUE, aggregate = FALSE, version="local")
# site_build("../sdc.broadband.alga_dev", serve = TRUE, open_after = TRUE, aggregate = FALSE)
