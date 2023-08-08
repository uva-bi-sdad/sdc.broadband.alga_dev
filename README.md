# sdc.broadband.alga_dev
Example repository of putting smaller sample data repositories together

```mermaid
graph LR;
%% Median Price for Internet in 2022
           med_int_price[<a href='https://advocacy.consumerreports.org/wp-content/uploads/2022/11/FINAL.report-broadband.november-17-2022-2.pdf'>Median Internet Price 2022</a>];
           med_int_price--75$-->avg_nat((75/B19013_001</br>*100));
           B19013_001-->avg_nat;

%% ACS things:
subgraph ACS_G["sdc.broadband.acs"]
           ACS[<a href='https://www.census.gov/programs-surveys/acs'>ACS</a>];
           year=2021-->ACS;
           ACS--B28001_001-->B28001_001["Estimate!!Total: TYPES OF COMPUTERS IN HOUSEHOLD"];
           ACS--B28001_002-->B28001_002["Estimate!!Total:!!<br/>Has one or more types of computing devices:"];
           ACS--B28002_001-->B28002_001["Estimate!!Total: PRESENCE AND TYPES OF INTERNET <br/> SUBSCRIPTIONS IN HOUSEHOLD"];
           ACS--B28002_004-->B28002_004["Estimate!!Total:!!<br/>With an Internet subscription!!Broadband of any type"];
           ACS--B28002_007-->B28002_007["Estimate!!Total:!!With an Internet subscription!!</br>Broadband such as cable, fiber optic or DSL"];
           ACS--B28002_013-->B28002_013["Estimate!!Total:!!No Internet access"];
           ACS--B19013_001-->B19013_001["Estimate!!Total: MEDIAN HOUSEHOLD INCOME IN THE PAST 12 MONTHS <br/>(IN 2021 INFLATION-ADJUSTED DOLLARS)"];
end

%% Broadbandnow things:
subgraph BBN_G["sdc.broadband.broadbandnow"]
           Broadbandnow[<a href='https://broadbandnow.com/'>Broadbandnow</a>];
           query_year=2023-->Broadbandnow;
           Broadbandnow-->speed;
           Broadbandnow-->down_up;
           Broadbandnow-->name;
           Broadbandnow-->type;
           Broadbandnow-->address;
           Broadbandnow-->price;
end

%% Ookla things:
subgraph OOKLA_G["sdc.broadband.ookla"]
           Ookla[<a href='https://www.ookla.com/ookla-for-good/open-data'>Ookla</a>];
           year=2022-->Ookla;
           Ookla-->avg_d_mbps;
           Ookla-->avg_u_mbps;
           Ookla-->tests;
           Ookla-->devices;
           Ookla-->q;
           Ookla-->year;
end

%% Calculations
           q -.-> dev(("sum(devices)/4q"));
           year -.-> dev;
           devices --> dev;
           q -.-> download(("sum(avg_d_mbps)/4q * </br>device_in_geo_level/ device_in_county"));
           year -.-> download;
           devices -.-> download;
           avg_d_mbps --> download;
           q -.-> upload(("sum(avg_u_mbps)/4q * </br>device_in_geo_level/ device_in_county"));
           year -.-> upload;
           devices -.-> upload;
           %% step3_generalized.Rmd:  sum(upload_devices * devices, na.rm = T) / sum(devices, na.rm = T), (Why do we need this? Isn't it multiplying the sum of upload speed by 1
           %% upon further inspection: above_20_up<-- pnorm(20, md_merged_data_up_devices$upload_devices, md_merged_data_up_devices$sd_county_up_devices, lower.tail = F) * 100 # a density distribution where mean is the upload devices, and standard deviation is equal to the sd_county_up_devices
           %% perc_w_int_above_20_up_using_devices <-- above_20_up
           avg_u_mbps --> upload;
           download -- avg_down_using_devices --> avg_down_using_devices_node["Average download speed weighted by number of devices"];
           upload -- avg_up_using_devices --> avg_up_using_devices_node["Average upload speed weighted by number of devices"];
           dev -- devices --> devices_node["The number of unique devices accessing Ookla Internet speed tests"];

           price --> perc_income_min_price_100(("min(price| upload &</br> speed >= 100 Mbps)/B19013_001"))
           B19013_001 --> perc_income_min_price_100;
           speed -.-> perc_income_min_price_100;
           down_up -.-> perc_income_min_price_100;

           perc_income_min_price_100 -- perc_income_min_price_100 --> perc_income_min_price_100_node["The minimum price for fast internet (100 MB/s upload)</br> as a percentage of median household income"];
           avg_nat -- perc_income_avg_nat_package -->perc_income_avg_nat_package_node["The national average price for internet ($75)</br> as a percentage of median household income"];
           B28001_001 --> perc_hh_without_compdev_c;
           B28001_002 --> perc_hh_without_compdev_c;
           perc_hh_without_compdev_c(("(B28001_001-B28001_002)</br>/B28001_001*100"));
           perc_hh_without_compdev_c -- perc_hh_without_compdev -->perc_hh_without_compdev_node["Percentage of the households self-reported</br> to not have a computer or device at home"];
           B28002_004 --> perc_hh_with_broadband_c((B28002_004/B28002_001*100));
           B28002_001 --> perc_hh_with_broadband_c;
           perc_hh_with_broadband_c -- perc_hh_with_broadband --> perc_hh_with_broadband_node["Percentage of households self-reported to have a broadband internet connection. </br> Broadband internet is defined as any type of internet other than a dial-up"];

           B19013_001 --> perc_income_min_price_25_c(("min(price| upload &</br> speed >= 25 Mbps)/B19013_001"));
           price --> perc_income_min_price_25_c;
           B19013_001 --> perc_income_min_price_25_c;
           speed -.-> perc_income_min_price_25_c;
           down_up -.-> perc_income_min_price_25_c;
           perc_income_min_price_25_c -- perc_income_min_price_25 -->perc_income_min_price_25_node["The minimum price for good internet (25 MB/s upload)</br> as a percentage of median household income"];

           %% On calculating perc_total_25_3_using_devices
           %%           with_internet = B28002_001 - B28002_013
           %%           perc_w_int_above_25_down_using_devices <- pnorm(25, va_merged_data_down_tests$download_tests,va_merged_data_down_tests$sd_county_down_tests, lower.tail = F) * 100
           %%           perc_w_int_above_25_down_using_devices = sum(pop_w_int_above_25_down_using_devices, na.rm = T) / sum(w_internet, na.rm = T), 
           %%           perc_total_above_25_down_using_devices = perc_w_int_above_25_down_using_devices * w_internet/tpopE,

subgraph OUTPUT_G["Outputs"]
           avg_down_using_devices_node;
           avg_up_using_devices_node;
           devices_node;
           perc_income_min_price_100_node;
           perc_income_avg_nat_package_node;
           perc_hh_without_compdev_node;
           perc_hh_with_broadband_node;
           perc_income_min_price_25_node;
           perc_w_int_100_20_using_devices_node;
           perc_total_100_20_using_devices_node;
           perc_w_int_25_3_using_devices_node;
           perc_total_25_3_using_devices_node;
end

%% Not yet complete
           TBA -- perc_w_int_100_20_using_devices --> perc_w_int_100_20_using_devices_node["Percent of the internet-connected population with a fast internet speed </br> (above 100/20 MB/s, able to stream HD video on multiple devices or download large files quickly)"];
           TBA -- perc_total_100_20_using_devices --> perc_total_100_20_using_devices_node["Percent of the total population with a fast internet speed </br>(above 100/20 MB/s, able to stream HD video on multiple devices or download large files quickly)"];
           TBA -- perc_w_int_25_3_using_devices --> perc_w_int_25_3_using_devices_node["Percent of the internet-connected population with a good internet speed </br> (above 25/3 MB/s, able to stream video or online game for one device)"];
           TBA -- perc_total_25_3_using_devices --> perc_total_25_3_using_devices_node["Percent of the total population with a good internet speed </br> (above 25/3 MB/s, able to stream video or online game for one device)"];
```

## Quickstart
- `git submodule update --recursive --remote` to download the submodules
- Run things in the `code` directory to generate the required datasets

## Example Data Output
```python
df = pd.read_csv('01007.csv.xz', dtype={'geoid':object})
df
           geoid                    measure  moe     value  year
0   010070100011  perc_income_min_price_100  NaN  0.066667  2023
1   010070100012  perc_income_min_price_100  NaN  0.088212  2023
2   010070100051  perc_income_min_price_100  NaN  0.051231  2023
3   010070100052  perc_income_min_price_100  NaN  0.082823  2023
4   010070100053  perc_income_min_price_100  NaN  0.037103  2023
5   010070100061  perc_income_min_price_100  NaN  0.036039  2023
6   010070100062  perc_income_min_price_100  NaN  0.044219  2023
7   010070100071  perc_income_min_price_100  NaN  0.053439  2023
8   010070100072  perc_income_min_price_100  NaN  0.050261  2023
9   010070100082  perc_income_min_price_100  NaN  0.040789  2023
10  010070100093  perc_income_min_price_100  NaN  0.089700  2023
11  010070100102  perc_income_min_price_100  NaN  0.047369  2023
12  010070100111  perc_income_min_price_100  NaN  0.031500  2023
```
