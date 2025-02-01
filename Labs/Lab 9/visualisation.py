import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests

# Download and open the file
url = "https://powietrze.gios.gov.pl/pjp/archives/downloadFile/563"
file_path = "air_quality.xlsx"

response = requests.get(url)
with open(file_path, "wb") as f:
    f.write(response.content)

data = pd.read_excel(file_path, sheet_name='PM2,5')

data['Rok'] = pd.to_numeric(data['Rok'], errors='coerce')
data = data.dropna(subset=['Rok'])
data['Rok'] = data['Rok'].astype(int)

filtered_data = data[
    (data['Czas uśredniania'] == '24g') &
    (data['Rok'] >= 2010) &
    (data['Rok'] <= 2023)
]

# Line plot for two selected stations
print(
"""
Wykres 1
Na wykresie przedstawiono zmiany średniego stężenia pyłów PM2,5 na przestrzeni lat 2010-2023 dla dwóch stacji
pomiarowych: Wrocławia i Szczecina. Widać, że stężenie PM2,5 we Wrocławiu było wyższe, jednakże poziom w obu
stacjach mniej więcej w podobnym czasie malał na przestrzeni lat 2010-2023, a róznica pomiędzy wykresami również
malała (teraz nie jest już tak duża, jak w 2100 roku).
"""
)

stations = ['ZpSzczec1Maj', 'DsWrocNaGrob']
station_data = filtered_data[filtered_data['Kod stacji'].isin(stations)]

plt.figure(figsize=(20, 6))
sns.lineplot(data=station_data, x='Rok', y='Średnia', hue='Kod stacji')
plt.title('Average PM2.5 Levels Over Time (Two Stations)')
plt.xlabel('Year')
plt.ylabel('Average PM2.5 (µg/m³)')
plt.legend(title='Station Code')
plt.grid(True)
plt.show()

# Boxplot for yearly PM2.5 distributions
print(
"""
Wykres 2
Wykres pudełkowy pokazuje rozkład średnich stężeń PM2,5 w Polsce z podziałem na lata 2010-2023. 
Widać, że w większości lat wartości stężeń PM2,5 w Polsce były stosunkowo zmienne, z większą zmiennością w latach
2010-2015. Średnie stężenie znacznie spadło na przestrzeni lat 2010-2023.
"""
)

plt.figure(figsize=(14, 7))
sns.boxplot(data=filtered_data, x='Rok', y='Średnia')
plt.title('Yearly Distribution of PM2.5 Levels (All Stations)')
plt.xlabel('Year')
plt.ylabel('Average PM2.5 (µg/m³)')
plt.grid(True)
plt.show()

# Bar plot of PM2.5 exceedances by voivodeship
print(
"""
Wykres 3
Wykres słupkowy przedstawia liczbę przekroczeń normy PM2,5 (25 µg/m³) w latach 2010-2023 w różnych województwach
Polski. Przeważającą większość przekroczeń normy odnotowano w województwach małopolskim i śląskim, co może
wskazywać na wyższy poziom zanieczyszczeń powietrza w tych regionach. Dla pozostałych województw, liczby
przekroczeń są podobne.
"""
)
filtered_data = filtered_data.copy()
pm25_threshold = 25
filtered_data['Exceedance'] = filtered_data['Średnia'] > pm25_threshold

exceedance_sum = filtered_data.groupby('Województwo')['Exceedance'].sum()
exceedance_percent = filtered_data.groupby('Województwo')['Exceedance'].mean() * 100

plt.figure(figsize=(12, 6))
exceedance_sum.sort_values().plot(kind='bar', color='skyblue')
plt.title('Total PM2.5 Exceedances by Voivodeship (2010-2023)')
plt.xlabel('Voivodeship')
plt.ylabel('Number of Exceedances')
plt.xticks(rotation=45)
plt.grid(axis='y')
plt.show()

print(
"""
Wykres 4
Wykres słupkowy pokazuje procent przekroczeń normy PM2,5 w poszczególnych województwach. Najwyższy procent
przekroczeń występuje w województwach małopolskim i śląskim, jednakże różnica w procencie przekroczeń między
tymi dwoma województwami, a resztą województw nie jest tak duża, co różnica liczby przekroczeń z wykresu 3.
"""
)
plt.figure(figsize=(12, 6))
exceedance_percent.sort_values().plot(kind='bar', color='orange')
plt.title('Percentage of PM2.5 Exceedances by Voivodeship (2010-2023)')
plt.xlabel('Voivodeship')
plt.ylabel('Percentage of Exceedances (%)')
plt.xticks(rotation=45)
plt.grid(axis='y')
plt.show()