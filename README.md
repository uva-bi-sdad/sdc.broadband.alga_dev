# sdc.broadband.alga_dev
A repository for calculating and storing broadband measures for Alabama and Georgia counties

## Data pipeline
```mermaid
graph LR;
%% Median Price for Internet in 2022
           med_int_price[<a href='https://advocacy.consumerreports.org/wp-content/uploads/2022/11/FINAL.report-broadband.november-17-2022-2.pdf'>Median Internet Price 2022</a>];
           med_int_price--75$-->avg_nat((" "));
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
           q -.-> dev((" "));
           year -.-> dev;
           devices --> dev;
           q -.-> download((" "));
           year -.-> download;
           devices -.-> download;
           avg_d_mbps --> download;
           q -.-> upload((" "));
           year -.-> upload;
           devices -.-> upload;
           %% step3_generalized.Rmd:  sum(upload_devices * devices, na.rm = T) / sum(devices, na.rm = T), (Why do we need this? Isn't it multiplying the sum of upload speed by 1
           %% upon further inspection: above_20_up<-- pnorm(20, md_merged_data_up_devices$upload_devices, md_merged_data_up_devices$sd_county_up_devices, lower.tail = F) * 100 # a density distribution where mean is the upload devices, and standard deviation is equal to the sd_county_up_devices
           %% perc_w_int_above_20_up_using_devices <-- above_20_up
           avg_u_mbps --> upload;
           download -- avg_down_using_devices --> avg_down_using_devices_node["<a style='color:#00FF00'>Average download speed weighted by number of devices</a>"];
           upload -- avg_up_using_devices --> avg_up_using_devices_node["<a style='color:#00FF00'>Average upload speed weighted by number of devices</a>"];
           dev -- devices --> devices_node["<a style='color:#00FF00'>The number of unique devices accessing Ookla Internet speed tests</a>"];

           price --> perc_income_min_price_100((" "))
           B19013_001 --> perc_income_min_price_100;
           speed -.-> perc_income_min_price_100;
           down_up -.-> perc_income_min_price_100;

           perc_income_min_price_100 -- perc_income_min_price_100 --> perc_income_min_price_100_node["<a style='color:#00FF00'>The minimum price for fast internet (100 MB/s upload)</br> as a percentage of median household income</a>"];
           avg_nat -- perc_income_avg_nat_package -->perc_income_avg_nat_package_node["<a style='color:#00FF00'>The national average price for internet ($75)</br> as a percentage of median household income</a>"];
           B28001_001 --> perc_hh_without_compdev_c;
           B28001_002 --> perc_hh_without_compdev_c;
           perc_hh_without_compdev_c((" "));
           perc_hh_without_compdev_c -- perc_hh_without_compdev -->perc_hh_without_compdev_node["<a style='color:#00FF00'>Percentage of the households self-reported</br> to not have a computer or device at home</a>"];
           B28002_004 --> perc_hh_with_broadband_c((" "));
           B28002_001 --> perc_hh_with_broadband_c;
           perc_hh_with_broadband_c -- perc_hh_with_broadband --> perc_hh_with_broadband_node["<a style='color:#00FF00'>Percentage of households self-reported to have a broadband internet connection. </br> Broadband internet is defined as any type of internet other than a dial-up</a>"];

           B19013_001 --> perc_income_min_price_25_c((" "));
           price --> perc_income_min_price_25_c;
           speed -.-> perc_income_min_price_25_c;
           down_up -.-> perc_income_min_price_25_c;
           perc_income_min_price_25_c -- perc_income_min_price_25 -->perc_income_min_price_25_node["<a style='color:#00FF00'>The minimum price for good internet (25 MB/s upload)</br> as a percentage of median household income</a>"];

           %% On calculating perc_total_25_3_using_devices
           %%           with_internet = B28002_001 - B28002_013
           %%           The probability that 25 Mbps is greater than a randomly drawn value in the known samples, P[X>x], fitted to a normal distribution
           %%           perc_w_int_above_25_down_using_devices <- pnorm(25, va_merged_data_down_tests$download_tests,va_merged_data_down_tests$sd_county_down_tests, lower.tail = F) * 100
           %%           perc_w_int_above_25_down_using_devices = sum(pop_w_int_above_25_down_using_devices, na.rm = T) / sum(w_internet, na.rm = T), 
           %%           perc_total_above_25_down_using_devices = perc_w_int_above_25_down_using_devices * w_internet/B28002_001

           B28002_001 --> perc_w_int_100_20_using_devices_c((" "));
           B28002_013 --> perc_w_int_100_20_using_devices_c;
           avg_d_mbps --> perc_w_int_100_20_using_devices_c;
           perc_w_int_100_20_using_devices_c -- perc_w_int_100_20_using_devices --> perc_w_int_100_20_using_devices_node["Percent of the internet-connected population with a fast internet speed </br> (above 100 Mbps Download and  20 Mbps Upload, able to stream HD video on multiple devices or download large files quickly)"];

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

subgraph LEGEND["Legend"]
           completed["<a style='color:#00FF00'>Completed</a>"];
           %% under_scrutiny["<a style='color:#FFA500'>Under Scrutiny</a>"];
end

%% Not yet complete
           TBA -- perc_total_100_20_using_devices --> perc_total_100_20_using_devices_node["Percent of the total population with a fast internet speed </br>(above 100/20 MB/s, able to stream HD video on multiple devices or download large files quickly)"];
           TBA -- perc_w_int_25_3_using_devices --> perc_w_int_25_3_using_devices_node["Percent of the internet-connected population with a good internet speed </br> (above 25/3 MB/s, able to stream video or online game for one device)"];
           TBA -- perc_total_25_3_using_devices --> perc_total_25_3_using_devices_node["Percent of the total population with a good internet speed </br> (above 25/3 MB/s, able to stream video or online game for one device)"];
```

## Methods for calculating measures

For the following measures, the geography is represented by $g$; the geography at a higher highest summary level is represented by $\textbf{g}$. At the lowest geography level, they are equivalent.

### avg_up_using_devices
```math
\textbf{u} = \frac{\text{Total upload speed of all devices}}{\text{Total number of devices}} = {\frac{\sum_{g}\text{Ookla}_{\text{upload},g}*\text{Ookla}_{\text{number of devices},g}}{\text{Ookla}_{\text{number of devices},\textbf{g}}}}
```

### devices
```math
n = \sum_{g}{\text{Ookla}_{\text{number of devices},g}}
```

### avg_down_using_devices
```math
\textbf{d} = \frac{\text{Total download speed of all devices}}{\text{Total number of devices}} =
{\frac{\sum_{g}\text{Ookla}_{\text{download},g}*\text{Ookla}_{\text{number of devices},g}}{\text{Ookla}_{\text{number of devices},\textbf{g}}}}
```

### perc_income_min_price_25
```math
\textbf{p} = \frac{\text{Percentage of income for minimum download speed}\ge\text{25 Mbps price}}{\text{Total number of geographies}}* 100 =
\prod_{g}{\frac{\min_{\text{price}}(\text{Broadbandnow}_{(\text{download}\ge 25\text{mbps}, g)})*12}{\text{B19013\_001}_g}} * 100
```

### perc_income_min_price_100
```math
\textbf{p} = \frac{\text{Percentage of income for minimum download speed}\ge\text{100 Mbps price}}{\text{Total number of geographies}}*100=
\prod_{g}{\frac{\min_{\text{price}}(\text{Broadbandnow}_{(\text{download}\ge 100\text{mbps}, g)})*12}{\text{B19013\_001}_g}} * 100
```

### perc_income_avg_nat_package
```math
\textbf{p} = \frac{\text{National average for internet}}{\text{Median household Income}}* 100 = \prod_{g}{\frac{75*12}{\text{B19013\_001}_g}} * 100
```

### perc_hh_without_compdev
```math
\textbf{p} = \frac{\text{Total types of computers in household} - \text{Has one or more types of computing devices}}{\text{Total types of computers in household}}* 100 =

\prod_{g}{\frac{(\text{B28001\_001}_g-\text{B28001\_002}_g)}
{\text{B28001\_001}_g}} * 100
```

### perc_hh_with_broadband
```math
\textbf{p} = \frac{\text{Total with an internet subscription Broadband of any type}}{\text{Total presence and types of internet subscriptions in household}}* 100 =

\prod_{g}{\frac{\text{B28002\_004}_g}
{\text{B28002\_001}_g}} * 100
```

### perc_w_int_100_20_using_devices
```math
\textbf{p} = \text{Probability}_{g \ge \text{100 Mbps download speed}} *  \text{Probability}_{g \ge \text{20 Mbps upload speed}} * \frac{\text{Total internet-connected population}_g}{\text{Total internet-connected population}_{\textbf{g}}}* 100  =

\prod_{g}\frac{P[\text{Ookla}_{\text{download}, g} \ge 100]*P[\text{OOkla}_{\text{upload}, g} \ge 20](\text{B28002\_001}_g - \text{B28002\_013}_g)}{(\text{B28002\_001}_\textbf{g} - \text{B28002\_013}_\textbf{g})} * 100
```

### perc_w_int_25_3_using_devices
```math
\textbf{p} = \text{Probability}_{g \ge \text{25 Mbps download speed}} *  \text{Probability}_{g \ge \text{3 Mbps upload speed}} * \frac{\text{Total internet-connected population}_g}{\text{Total internet-connected population}_{\textbf{g}}}* 100  =

\prod_{g}\frac{P[\text{Ookla}_{\text{download}, g} \ge 25]*P[\text{OOkla}_{\text{upload}, g} \ge 3](\text{B28002\_001}_g - \text{B28002\_013}_g)}{(\text{B28002\_001}_\textbf{g} - \text{B28002\_013}_\textbf{g})} * 100
```


## Quickstart
- `git submodule update --recursive --remote` to download the submodules
- Run `python prepare_broadband_dataset.py` to generate the dataset
- Run `build.R` to generate the dashboard

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
