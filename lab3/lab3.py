#Лабораторна робота №3. Виконала студентка групи ФБ-35 Дедяєва Софія
import pandas as pd
import urllib.request
from datetime import datetime
import os
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

print("Setup Complete")

def csv_down(index):
    dir_files = os.listdir('C:/Dediaieva/Python/csv_prov')
    try:
        for x in dir_files:
            if int(x.split('_')[2]) == index:
                print(f'-File {index} already downloaded')
                return
    except IndexError:
        print('Bad name for file')
    url=f"https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={index}&year1=1981&year2=2024&type=Mean"
    vhi_url = urllib.request.urlopen(url)
    now = datetime.now()
    date_and_time = now.strftime("%d%m%Y%H%M%S")
    out = open(f'C:/Dediaieva/Python/csv_prov/vhi_id_{index}_{date_and_time}.csv', 'wb')
    out.write(vhi_url.read())
    out.close()
    print(f'+File {index} downloaded')
#lab3
for i in range(1,26):
    csv_down(i)

def data_in_frame(path):
    headers = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'empty']
    dataframes = []
    for filename in os.listdir(path):
        if not filename.startswith("vhi_id_"):
            continue
        index = filename.split('_')[2]
        filepath = os.path.join(path, filename)
        df = pd.read_csv(filepath, header=1, names=headers)
        df['Year'] = df['Year'].astype(str).str.extract(r'(\d{4})')[0]
        df = df[df['Year'].notna()]
        df = df.drop(df.loc[df['VHI'] == -1].index)
        df['Region'] = index
        df = df.drop(columns='empty')
        df['Year'] = df['Year'].astype(int)
        df['Week'] = df['Week'].astype(int)
        df['Region'] = df['Region'].astype(int)
        dataframes.append(df)
    return pd.concat(dataframes, ignore_index=True).drop_duplicates().reset_index(drop=True)

data_frame = data_in_frame('C:/Dediaieva/Python/csv_prov')
print(data_frame)

def convert_region_indices(dataframe, column="Region"):
    region_mapping = {
        24: 1, 25: 2, 5: 3, 6: 4, 27: 5, 23: 6, 26: 7, 7: 8,
        11: 9, 13: 10, 14: 11, 15: 12, 16: 13, 17: 14, 18: 15,
        19: 16, 21: 17, 22: 18, 8: 19, 9: 20, 10: 21, 1: 22, 3: 23,
        2: 24, 4: 25, 12: 26, 20: 27
    }
    dataframe[column] = dataframe[column].map(region_mapping).fillna(dataframe[column]).astype(int)
    return dataframe

converted_datafr = convert_region_indices(data_frame)
print(converted_datafr)

def vhi_year(df, index, year):
    return df[(df["Region"] == index) & (df["Year"] == year)]['VHI']

print(vhi_year(converted_datafr, 2, 1996))

def min_max(df, index,year):
    max_vhi = vhi_year(df, index, year).max()
    min_vhi = vhi_year(df, index, year).min()
    mean_vhi = vhi_year(df, index, year).mean()
    median_vhi = vhi_year(df, index, year).median()
    print(f'### Region: {index} ###\nMax vhi: {max_vhi}\nMin vhi: {min_vhi}\nMean vhi: {round(mean_vhi, 2)}\nMedian vhi: {round(median_vhi,2)}')

for x in range(1,29):
    min_max(converted_datafr, x, 2000)

def vhi_row_year_region(df, regions, start_year, end_year):
    for region in regions:
        print(f"Region {region}:")
        vhi = df[(df['Region'] == region) & (df['Year'].between(start_year, end_year))]
        if not vhi.empty:
            print(vhi)
        else:
            print(f"No data available for region {region} for years {start_year}-{end_year}")
    print("\n")

vhi_row_year_region(converted_datafr, [1,6,2], 2000, 2005)

def drought_stats(df, percent):
    total_regions = df['Region'].nunique()
    extreme_drought_data = {}
    for year in range(df['Year'].min(), df['Year'].max() + 1):
        affected_regions = df[(df['Year'] == year) & (df['VHI'] < 15)]
        unique_regions = affected_regions['Region'].unique()
        if len(unique_regions) > total_regions * (percent / 100):
            extreme_drought_data[year] = {
                "regions": list(unique_regions),
                "VHI_values": list(affected_regions['VHI'])
            }
    if extreme_drought_data:
        print(f"Years with extreme drought affecting more than {percent}% of the regions in Ukraine:")
        for year, data in extreme_drought_data.items():
            print(f"Year: {year}\nRegions: {data['regions']}\nVHI: {data['VHI_values']}\n")
    else:
        print(f"No years found where more than {percent}% of the regions experienced extreme drought.")

drought_stats(converted_datafr, 10)

st.title("Аналіз показників VCI/TCI/VHI")

province_dict = {
    1: "Вінницька", 2: "Волинська", 3: "Дніпропетровська", 4: "Донецька", 5: "Житомирська",
    6: "Закарпатська", 7: "Запорізька", 8: "Івано-Франківська", 9: "Київська", 10: "Кіровоградська",
    11: "Луганська", 12: "Львівська", 13: "Миколаївська", 14: "Одеська", 15: "Полтавська",
    16: "Рівненська", 17: "Сумська", 18: "Тернопільська", 19: "Харківська", 20: "Херсонська",
    21: "Хмельницька", 22: "Черкаська", 23: "Чернівецька", 24: "Чернігівська", 25: "АР Крим",
    26: "м. Київ", 27: "м. Севастополь"
}

if 'reset' not in st.session_state:
    st.session_state.reset = False
if 'choosen_value' not in st.session_state or st.session_state.reset:
    st.session_state.choosen_value = "VCI"
    st.session_state.region = list(province_dict.values())[0]
    st.session_state.weeks_range = (1, 15)
    st.session_state.years_range = (2000, 2005)
    st.session_state.sort_asc = False
    st.session_state.sort_desc = False
    st.session_state.reset = False

col1, col2 = st.columns([1, 2])

with col1:
    choosen_value = st.selectbox("Оберіть показник", ["VCI", "TCI", "VHI"], key="choosen_value")
    region = st.selectbox("Оберіть область", options=list(province_dict.values()), key="region")
    weeks_range = st.slider("Інтервал тижнів", 1, 52, key="weeks_range")
    years_range = st.slider("Інтервал років", 1982, 2023, key="years_range")
    sort_asc = st.checkbox("Сортувати за зростанням", key="sort_asc")
    sort_desc = st.checkbox("Сортувати за спаданням", key="sort_desc")

    if sort_asc and sort_desc:
        st.warning("Не можна обрати обидва сортування одночасно")

    if st.button("Скинути фільтри"):
        st.session_state.reset = True

with col2:
    region_index = list(province_dict.keys())[list(province_dict.values()).index(region)]
    filtered = converted_datafr[
        (converted_datafr['Region'] == region_index) &
        (converted_datafr['Week'].between(*weeks_range)) &
        (converted_datafr['Year'].between(*years_range))
    ]

    if sort_asc and not sort_desc:
        filtered = filtered.sort_values(by=choosen_value, ascending=True)
    elif sort_desc and not sort_asc:
        filtered = filtered.sort_values(by=choosen_value, ascending=False)

    tab1, tab2, tab3 = st.tabs(["Таблиця", "Графік", "Порівняння по регіонах"])

    with tab1:
        st.write("### Відфільтровані дані", filtered[["Year", "Week", choosen_value, "Region"]])

    with tab2:
        if not filtered.empty:
            plt.figure(figsize=(10, 5))
            sns.lineplot(data=filtered, x="Week", y=choosen_value, marker="o")
            plt.title(f"{choosen_value} у {region} ({years_range[0]} - {years_range[1]})")
            plt.xlabel("Тиждень")
            plt.ylabel(choosen_value)
            st.pyplot(plt)
        else:
            st.info("Немає даних для обраних фільтрів.")

    with tab3:
        compare_df = converted_datafr[
            (converted_datafr['Week'].between(*weeks_range)) &
            (converted_datafr['Year'].between(*years_range))
            ]

        if not compare_df.empty:
            plt.figure(figsize=(12, 6))
            mean_df = compare_df.groupby(['Region', 'Week'])[choosen_value].mean().reset_index()
            mean_df["RegionName"] = mean_df["Region"].map(province_dict)
            sns.lineplot(data=mean_df, x="Week", y=choosen_value, hue="RegionName", linewidth=1)
            selected_region_name = province_dict[region_index]
            selected_region_df = mean_df[mean_df['RegionName'] == selected_region_name]
            sns.lineplot(data=selected_region_df, x="Week", y=choosen_value, color="black", linewidth=3,
                         label="Обрана область")
            plt.title(f"Порівняння {choosen_value} між регіонами ({years_range[0]}–{years_range[1]})")
            plt.xlabel("Тиждень")
            plt.ylabel(choosen_value)
            plt.legend(title="Області", bbox_to_anchor=(1, 1))
            st.pyplot(plt)
        else:
            st.info("Немає даних для порівняння")
 #Лабораторна робота