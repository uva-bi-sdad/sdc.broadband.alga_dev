# sdc.broadband.alga_dev
Example repository of putting smaller sample data repositories together

```mermaid
graph LR;
           TBA -- avg_down_using_devices --> markdown12["Average download speed weighted by number of devices"];
           TBA -- avg_up_using_devices --> markdown11["Average upload speed weighted by number of devices"];
           TBA -- devices --> markdown10["The number of unique devices accessing Ookla Internet speed tests"];
           TBA -- perc_w_int_100_20_using_devices --> markdown9["Percent of the internet-connected population with a fast internet speed </br> (above 100/20 MB/s, able to stream HD video on multiple devices or download large files quickly)"];
           TBA -- perc_total_100_20_using_devices --> markdown8["Percent of the total population with a fast internet speed </br>(above 100/20 MB/s, able to stream HD video on multiple devices or download large files quickly)"];
           TBA -- perc_w_int_25_3_using_devices --> markdown7["Percent of the internet-connected population with a good internet speed </br> (above 25/3 MB/s, able to stream video or online game for one device)"];
           TBA -- perc_total_25_3_using_devices --> markdown6["Percent of the total population with a good internet speed </br> (above 25/3 MB/s, able to stream video or online game for one device)"];
           TBA -- perc_hh_without_compdev -->markdown5["Percentage of the households self-reported</br> to not have a computer or device at home"];
           TBA -- perc_hh_with_broadband --> markdown4["Percentage of households self-reported to have a broadband internet connection. </br> Broadband internet is defined as any type of internet other than a dial-up"];
           TBA -- perc_income_min_price_100 -->markdown3["The minimum price for fast internet (100 MB/s upload)</br> as a percentage of median household income"];
           TBA -- perc_income_min_price_25 -->markdown2["The minimum price for good internet (25 MB/s upload)</br> as a percentage of median household income"];
           TBA -- perc_income_avg_nat_package -->markdown1["The national average price for internet ($64)</br> as a percentage of median household income"];
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
