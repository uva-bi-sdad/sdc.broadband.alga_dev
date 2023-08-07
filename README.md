# sdc.broadband.alga_dev
Example repository of putting smaller sample data repositories together

```mermaid
graph LR;
%% Median Price for Internet in 2022
           med_int_price[<a href='https://advocacy.consumerreports.org/wp-content/uploads/2022/11/FINAL.report-broadband.november-17-2022-2.pdf'>Median Internet Price 2022</a>];
           med_int_price--75$-->avg_nat((mean*100));
           B19013_001-->avg_nat((mean*100));

%% ACS things:
           year=2021-->ACS;
           ACS--B19013_001-->B19013_001["MEDIAN HOUSEHOLD INCOME IN THE PAST 12 MONTHS <br/>(IN 2021 INFLATION-ADJUSTED DOLLARS)"];
           ACS--B28002_001-->B28002_001["PRESENCE AND TYPES OF INTERNET <br/> SUBSCRIPTIONS IN HOUSEHOLD"];
           ACS--B28001_002-->B28001_002["Estimate!!Total:!!<br/>Has one or more types of computing devices:"];
           ACS--B28002_004-->B28002_004["Estimate!!Total:!!<br/>With an Internet subscription!!Broadband of any type"];
           ACS--B28002_007-->B28002_007["Estimate!!Total:!!With an Internet subscription!!</br>Broadband such as cable, fiber optic or DSL"];
           ACS--B28002_013-->B28002_013["Estimate!!Total:!!No Internet access"];

%% Broadbandnow things:
           query_year=2023-->Broadbandnow;
           Broadbandnow-->speed;
           Broadbandnow-->down_up;
           Broadbandnow-->price;
           Broadbandnow-->name;
           Broadbandnow-->type;
           Broadbandnow-->address;

%% Ookla things:
           year=2022-->Ookla;
           Ookla-->avg_d_mbps;
           Ookla-->avg_u_mbps;
           Ookla-->tests;
           Ookla-->devices;
           Ookla-->q;
           Ookla-->year;

%% Calculations
           q -.-> dev((mean));
           year -.-> dev((mean));
           devices --> dev((mean));
           q -.-> download((mean));
           year -.-> download((mean));
           avg_d_mbps --> download((mean));
           q -.-> upload((mean));
           year -.-> upload((mean));
           avg_u_mbps --> upload((mean));
           download((mean)) -- avg_down_using_devices --> markdown12["Average download speed weighted by number of devices"];
           upload((mean)) -- avg_up_using_devices --> markdown11["Average upload speed weighted by number of devices"];
           dev((mean)) -- devices --> markdown10;
           markdown10["The number of unique devices accessing Ookla Internet speed tests"];

           price --> perc_income_min_price_100((mean*100))
           B19013_001 --> perc_income_min_price_100((mean*100))
           speed -.-> perc_income_min_price_100((mean*100))
           down_up -.-> perc_income_min_price_100((mean*100))

           perc_income_min_price_100((mean*100)) -- perc_income_min_price_100 --> markdown3["The minimum price for fast internet (100 MB/s upload)</br> as a percentage of median household income"];
           avg_nat((mean*100)) -- perc_income_avg_nat_package -->markdown1["The national average price for internet ($75)</br> as a percentage of median household income"];

%% Not yet complete
           TBA -- perc_w_int_100_20_using_devices --> markdown9["Percent of the internet-connected population with a fast internet speed </br> (above 100/20 MB/s, able to stream HD video on multiple devices or download large files quickly)"];
           TBA -- perc_total_100_20_using_devices --> markdown8["Percent of the total population with a fast internet speed </br>(above 100/20 MB/s, able to stream HD video on multiple devices or download large files quickly)"];
           TBA -- perc_w_int_25_3_using_devices --> markdown7["Percent of the internet-connected population with a good internet speed </br> (above 25/3 MB/s, able to stream video or online game for one device)"];
           TBA -- perc_total_25_3_using_devices --> markdown6["Percent of the total population with a good internet speed </br> (above 25/3 MB/s, able to stream video or online game for one device)"];
           TBA -- perc_hh_without_compdev -->markdown5["Percentage of the households self-reported</br> to not have a computer or device at home"];
           TBA -- perc_hh_with_broadband --> markdown4["Percentage of households self-reported to have a broadband internet connection. </br> Broadband internet is defined as any type of internet other than a dial-up"];

           TBA -- perc_income_min_price_25 -->markdown2["The minimum price for good internet (25 MB/s upload)</br> as a percentage of median household income"];
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
