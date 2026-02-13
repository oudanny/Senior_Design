import pandas as pd 
import re

csv = pd.read_csv('forecasting/monthly_cumulative_volumes.csv')
# =================================================

def extract_code(s):
    match = re.search(r'\b([A-Z])\s*(\d+)WB\b', s)
    if match:
        return f"{match.group(1)}{match.group(2)}"
    return None

csv['WellName'] = csv['WellName'].apply(extract_code)
csv = csv.rename(columns={'WellName': 'Well'})
new_row = {"Well": 'Name', "prod_date": 'YYYY-MM-DD', "Oil": 'Bbl/Mo', "Gas": 'MCF/Mo', "Water": 'BBl/Mo'}
# HM_csv = pd.concat([pd.DataFrame([new_row]), csv], ignore_index=True)


csv.to_csv('forecasting/HM_norm_monthly_cum.prd', index=False)