import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

daily_rate = pd.read_csv('forecasting/HM_norm_daily_rates.prd')
daily_rate = daily_rate[daily_rate['Well'] != 'Name']  # Remove the header row if it exists in the data
print(daily_rate.head())
daily_rate['prod_date'] = pd.to_datetime(daily_rate['prod_date'])
daily_rate['Oil_rate'] = pd.to_numeric(daily_rate['Oil_rate'], errors='coerce').round().astype('Int64')
daily_rate['Gas_rate'] = pd.to_numeric(daily_rate['Gas_rate'], errors='coerce').round().astype('Int64')
daily_rate['Water_rate'] = pd.to_numeric(daily_rate['Water_rate'], errors='coerce').round().astype('Int64')

fig, ax = plt.subplots(figsize=(20, 6), layout='constrained')
sns.lineplot(data=daily_rate, x='prod_date', y='Oil_rate', hue='Well', ax=ax, marker='o')
ax.set_title('Daily Oil Rate')
ax.set_xlabel('Production Date')
ax.set_ylabel('STB/d')
plt.savefig('forecasting/plots/norm_daily_rates_phase_oil.png')
plt.close()

fig, ax = plt.subplots(figsize=(20, 6), layout='constrained')
sns.lineplot(data=daily_rate, x='prod_date', y='Gas_rate', hue='Well', ax=ax, marker='o')
ax.set_title('Daily Gas Rate')
ax.set_xlabel('Production Date')
ax.set_ylabel('MSCF/d')
plt.savefig('forecasting/plots/norm_daily_rates_phase_gas.png')
plt.close()

fig, ax = plt.subplots(figsize=(20, 6), layout='constrained')
sns.lineplot(data=daily_rate, x='prod_date', y='Water_rate', hue='Well', ax=ax, marker='o')
ax.set_title('Daily Water Rate')
ax.set_xlabel('Production Date')
ax.set_ylabel('STB/d')
plt.savefig('forecasting/plots/norm_daily_rates_phase_water.png')
plt.close()