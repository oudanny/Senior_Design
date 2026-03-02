import pandas as pd

# monthly_rate_df = pd.read_csv('forecasting/norm_monthly_rates.csv')
monthly_rate_df = pd.read_csv('forecasting/wolfcamp_bupper_forecast.csv')

# Find days in each month for each prod_date
monthly_rate_df['prod_date'] = pd.to_datetime(monthly_rate_df['prod_date'])
monthly_rate_df['days_in_month'] = monthly_rate_df['prod_date'].dt.days_in_month
# Convert monthly rates to daily rates
monthly_rate_df['Oil_rate'] = monthly_rate_df['Oil_rate'] / monthly_rate_df['days_in_month']
monthly_rate_df['Gas_rate'] = monthly_rate_df['Gas_rate'] / monthly_rate_df['days_in_month']
monthly_rate_df['Water_rate'] = monthly_rate_df['Water_rate'] / monthly_rate_df['days_in_month']
# Drop the 'days_in_month' column as it's no longer needed
monthly_rate_df = monthly_rate_df.drop(columns=['days_in_month'])
# Save the updated dataframe
monthly_rate_df.to_csv('forecasting/norm_daily_rates.csv', index=False)
print("Monthly rates have been converted to daily rates and saved to 'forecasting/norm_daily_rates.csv'.")