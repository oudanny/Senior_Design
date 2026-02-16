import pandas as pd 
import re

# csv = pd.read_csv('forecasting/monthly_cumulative_volumes.csv')
# csv = pd.read_csv('forecasting/norm_monthly_rates.csv')
csv = pd.read_csv('forecasting/norm_daily_rates.csv')
# =================================================

def extract_code(s):
    match = re.search(r'\b([A-Z])\s*(\d+)WB\b', s)
    if match:
        return f"{match.group(1)}{match.group(2)}"
    return None

csv['WellName'] = csv['WellName'].apply(extract_code)
csv = csv.rename(columns={'WellName': 'Well'})
# new_row = {"Well": 'Name', "prod_date": 'YYYY-MM-DD', "Oil_rate": 'Bbl/Mo', "Gas_rate": 'MCF/Mo', "Water_rate": 'BBl/Mo'}
new_row = {"Well": 'Name', "prod_date": 'YYYY-MM-DD', "Oil_rate": 'STB/d', "Gas_rate": 'MCF/d', "Water_rate": 'STB/d'}

HM_csv = pd.concat([pd.DataFrame([new_row]), csv], ignore_index=True)


HM_csv.to_csv('forecasting/HM_norm_daily_rates.prd', index=False)