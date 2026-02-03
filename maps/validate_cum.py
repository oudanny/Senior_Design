import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns


monthly_data = pd.read_csv(r'C:\Users\txjam\Documents\homework\design\forecasting\ResEcon_MoProd.csv')
# norm_prod = pd.read_excel(r'C:\Users\txjam\Documents\homework\design\forecasting\normalized-TF-prod.xlsx')
print(monthly_data.columns.tolist())

normalized_cum_volumes = monthly_data[['ENVInterval','WellName','Norm. Cum Oil 12mo (bbl)', 'Norm. Cum. Gas 12mo (Mcf)','Norm. Cum. Water 12mo (bbl)']]
normalized_cum_volumes = normalized_cum_volumes.groupby('WellName').first().reset_index()
well_counts = normalized_cum_volumes.groupby('ENVInterval').size().reset_index(name='Well Count')
print("\nNumber of Wells by ENV Interval:")
print(well_counts)

fig,ax = plt.subplots(3,1, figsize=(10,15))
sns.boxplot(data=normalized_cum_volumes, x='ENVInterval', y='Norm. Cum Oil 12mo (bbl)', ax=ax[0])
ax[0].set_title('Normalized Cumulative Oil Volume in 12 months by ENV Interval')
ax[0].set_ylabel('10k ft Lateral Normalized Cumulative Oil Volume (bbl)')
ax[0].set_xlabel('Formation')

sns.boxplot(data=normalized_cum_volumes, x='ENVInterval', y='Norm. Cum. Gas 12mo (Mcf)', ax=ax[1])
ax[1].set_title('Normalized Cumulative Gas Volume in 12 months by ENV Interval')
ax[1].set_ylabel('10k ft Lateral Normalized Cumulative Gas Volume (Mcf)')
ax[1].set_xlabel('Formation')

sns.boxplot(data=normalized_cum_volumes, x='ENVInterval', y='Norm. Cum. Water 12mo (bbl)', ax=ax[2])
ax[2].set_title('Normalized Cumulative Water Volume in 12 months by ENV Interval')
ax[2].set_ylabel('10k ft Lateral Normalized Cumulative Water Volume (bbl)')
ax[2].set_xlabel('Formation')





'''
['API_UWI', 'WellName', 'Latitude', 'Longitude', 'ENVInterval', 'LateralLength_FT', 
'SpudDate', 'CompletionDate', 'FirstProdDate', 'First3MonthGas_MCF', 'First3MonthOil_BBL', 
'First3MonthWater_BBL', 'First6MonthGas_MCF', 'First6MonthOil_BBL', 'First6MonthWater_BBL', 
'First9MonthGas_MCF', 'First9MonthOil_BBL', 'First9MonthWater_BBL', 'First12MonthGas_MCF', 
'First12MonthOil_BBL', 'First12MonthWater_BBL', 
'CumGas_MCF', 'CumOil_BBL', 'CumWater_BBL', 
'Norm. Cum. Water 3mo (bbl)', 'Norm. Cum. Water 6mo (bbl)', 
'Norm. Cum. Water 9mo (bbl)', 'Norm. Cum. Water 12mo (bbl)', 
'Norm. Cum. Water (bbl)', 'Norm. Cum. Oil 3mo (bbl)', 'Norm. Cum. Gas 3mo (Mcf)', 
'Norm. Cum Oil 6mo (bbl)', 'Norm. Cum. Gas 6mo (Mcf)', 'Norm. Cum. Oil 9mo (bbl)', 
'Norm. Cum Gas 9mo (Mcf)', 'Norm. Cum Oil 12mo (bbl)', 'Norm. Cum. Gas 12mo (Mcf)', 
'Norm. Cum. Oil (bbl)', 'Norm. Cum Gas (Mcf)', 'MonthNumber', 'ProdDate', 'MonthlyOil_BBL', 
'MonthlyGas_MCF', 'MonthlyWater_BBL']
'''

monthly_plotting_data = monthly_data[['ENVInterval','WellName','ProdDate','MonthlyOil_BBL','MonthlyGas_MCF','MonthlyWater_BBL']]
fig,ax = plt.subplots(3,1, figsize=(10,15))
sns.lineplot(data=monthly_plotting_data, x='ProdDate', y='MonthlyOil_BBL', hue='ENVInterval',markers='o', ax=ax[0])
ax[0].set_title('Monthly Oil Production by ENV Interval')
ax[0].set_ylabel('Monthly Oil Production (bbl)')
ax[0].set_xlabel('Production Date')

sns.lineplot(data=monthly_plotting_data, x='ProdDate', y='MonthlyGas_MCF', hue='ENVInterval',markers='o', ax=ax[1])
ax[1].set_title('Monthly Gas Production by ENV Interval')
ax[1].set_ylabel('Monthly Gas Production (Mcf)')
ax[1].set_xlabel('Production Date')

sns.lineplot(data=monthly_plotting_data, x='ProdDate', y='MonthlyWater_BBL',hue='WellName',markers='o', ax=ax[2])
ax[2].set_title('Monthly Water Production by ENV Interval')
ax[2].set_ylabel('Monthly Water Production (bbl)')
ax[2].set_xlabel('Production Date')
