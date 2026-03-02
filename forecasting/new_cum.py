import pandas as pd 
import pathlib 
import numpy as np
from scipy.optimize import curve_fit

path_to_data = "/workspaces/Senior_Design/forecasting/wolfcamp_bupper_prod_norm.csv"
df = pd.read_csv(path_to_data)

columns_to_convert = [
    'Norm. Cum. Water 3mo (bbl)', 'Norm. Cum. Water 6mo (bbl)',
    'Norm. Cum. Water 9mo (bbl)', 'Norm. Cum. Water 12mo (bbl)',
    'Norm. Cum. Oil 3mo (bbl)',  'Norm. Cum. Gas 3mo (Mcf)', 
    'Norm. Cum Oil 6mo (bbl)',   'Norm. Cum. Gas 6mo (Mcf)', 
    'Norm. Cum. Oil 9mo (bbl)',  'Norm. Cum Gas 9mo (Mcf)', 
    'Norm. Cum Oil 12mo (bbl)',  'Norm. Cum. Gas 12mo (Mcf)',
]

df = df[['WellName', 'FirstProdDate'] + columns_to_convert]
df['FirstProdDate'] = pd.to_datetime(df['FirstProdDate'])

long = df.melt(id_vars=["WellName", "FirstProdDate"], var_name="Variable", value_name="Cumulative")
long["Phase"] = long["Variable"].str.extract(r'(Water|Oil|Gas)')
long["Month"] = long["Variable"].str.extract(r'(\d+)').astype(int)
long = long.drop(columns="Variable")

final = long.pivot_table(
    index=["WellName", "FirstProdDate", "Month"],
    columns="Phase",
    values="Cumulative"
).reset_index()
final.columns.name = None

# ------------------------------------------------------------
# Exponential cumulative model (Arps b=0)
# ------------------------------------------------------------
def exp_cum_model(t, qi, D):
    return (qi / D) * (1 - np.exp(-D * t))

# ------------------------------------------------------------
# Fit + Forecast — one row per Well/Date/Month, one col per phase
# ------------------------------------------------------------
results = []

for (well, date), group in final.groupby(["WellName", "FirstProdDate"]):
    group = group.sort_values("Month")
    months = group["Month"].values
    months_full = np.arange(1, 13)

    # Build a dict keyed by month for this well
    month_rows = {m: {"WellName": well, "FirstProdDate": date, "Month": m} for m in months_full}

    for phase in ["Oil", "Gas", "Water"]:
        if phase not in group.columns:
            continue

        cum = group[phase].values
        if np.any(np.isnan(cum)):
            continue

        try:
            qi_guess = cum[0] / months[0]
            popt, _ = curve_fit(
                exp_cum_model, months, cum,
                p0=[qi_guess, 0.2],
                bounds=(0, np.inf),
                maxfev=10000
            )
            qi_fit, D_fit = popt

            rate_forecast = qi_fit * np.exp(-D_fit * months_full)
            cum_forecast  = exp_cum_model(months_full, qi_fit, D_fit)

            for m, q, c in zip(months_full, rate_forecast, cum_forecast):
                month_rows[m][f"{phase}_Rate"] = q
                month_rows[m][f"{phase}_Cum_ExpForecast"]  = c
                month_rows[m][f"{phase}_qi"] = qi_fit
                month_rows[m][f"{phase}_D"]  = D_fit

        except RuntimeError:
            continue

    results.extend(month_rows.values())

forecast_df = pd.DataFrame(results)

# Reorder columns nicely
meta_cols = ["WellName", "FirstProdDate", "Month"]
phase_cols = [c for c in forecast_df.columns if c not in meta_cols]
forecast_df = forecast_df[meta_cols + sorted(phase_cols)]
forecast_df["ProdDate"] = forecast_df.apply(
    lambda r: r["FirstProdDate"] + pd.DateOffset(months=(r["Month"] - 1)), axis=1
)

print(f'Forecast Cols : {forecast_df.columns.tolist()}')
output_cols = ['WellName','ProdDate','Gas_Rate', 'Oil_Rate', 'Water_Rate' ]

forecast_df = forecast_df[output_cols]
forecast_df = forecast_df.rename(columns={
    'ProdDate': 'prod_date',
    'Gas_Rate': 'Gas_rate',
    'Oil_Rate': 'Oil_rate',
    'Water_Rate': 'Water_rate'
})
forecast_df.to_csv("forecasting/wolfcamp_bupper_forecast.csv", index=False)

print(forecast_df.head())

Temple_Fork_D4 = forecast_df[forecast_df["WellName"] == "TEMPLE FORK 32-20 D 4WB"]
print(Temple_Fork_D4)

# import seaborn as sns
# import matplotlib.pyplot as plt

# fig,ax = plt.subplots()
# sns.lineplot(
#     data=Temple_Fork_D4,
#     x="Month",
#     y="Oil_Rate",
#     marker="o",
#     ax=ax
# )
# fig.savefig("forecasting/plots/Temple_Fork_D4_forecast.png", dpi=300)