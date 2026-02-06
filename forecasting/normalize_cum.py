import pandas as pd 
import numpy as np

df = pd.read_csv(r'forecasting/wolfcamp_bupper_prod_unnorm.csv')

columns_to_convert_from = [
    'First3MonthWater_BBL', 'First6MonthWater_BBL',
    'First9MonthWater_BBL', 'First12MonthWater_BBL',
    'First3MonthOil_BBL', 'First3MonthGas_MCF',
    'First6MonthOil_BBL', 'First6MonthGas_MCF',
    'First9MonthOil_BBL', 'First9MonthGas_MCF',
    'First12MonthOil_BBL', 'First12MonthGas_MCF',
]

columns_to_convert_to = [
    'Norm. Cum. Water 3mo (bbl)', 'Norm. Cum. Water 6mo (bbl)',
    'Norm. Cum. Water 9mo (bbl)', 'Norm. Cum. Water 12mo (bbl)',
    'Norm. Cum. Oil 3mo (bbl)', 'Norm. Cum. Gas 3mo (Mcf)',
    'Norm. Cum Oil 6mo (bbl)', 'Norm. Cum. Gas 6mo (Mcf)',
    'Norm. Cum. Oil 9mo (bbl)', 'Norm. Cum Gas 9mo (Mcf)',
    'Norm. Cum Oil 12mo (bbl)', 'Norm. Cum. Gas 12mo (Mcf)',
]
# Normalize cumulative production to 10,000 ft lateral length
normalization_factor = 10_000 / df['LateralLength_FT']

for from_col, to_col in zip(columns_to_convert_from, columns_to_convert_to):
    df[to_col] = df[from_col] * normalization_factor

# Save the normalized dataframe
df.to_csv('forecasting/wolfcamp_bupper_prod_norm.csv', index=False)