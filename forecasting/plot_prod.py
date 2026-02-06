import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------
# Load data
# -------------------------------------------------

cum_df = pd.read_csv(r'/workspaces/Senior_Design/forecasting/monthly_cumulative_volumes.csv')
rate_df = pd.read_csv(r'/workspaces/Senior_Design/forecasting/norm_monthly_rates.csv')
# -------------------------------------------------
# Prep dates
cum_df["prod_date"] = pd.to_datetime(cum_df["prod_date"])
rate_df["prod_date"] = pd.to_datetime(rate_df["prod_date"])

# Plot settings
phase_order = ["Gas", "Oil", "Water"]
phase_colors = {"Gas": "tab:blue", "Oil": "tab:orange", "Water": "tab:green"}

# Plot cumulative volumes by phase vs time (hue by WellName)
fig_cum, axes_cum = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
for ax, phase in zip(axes_cum, phase_order):
	phase_df = cum_df[cum_df["phase"] == phase]
	sns.lineplot(
		data=phase_df,
		x="prod_date",
		y="cum_prod",
		hue="WellName",
		marker="o",
		ax=ax,
		legend=False,
		color=phase_colors.get(phase),
	)
	ax.set_title(f"Cumulative Production - {phase}")
	ax.set_xlabel("Production Date")
	ax.set_ylabel("Cumulative Production")
fig_cum.tight_layout()
fig_cum.savefig(r'forecasting/plots/norm_cumulative_production.png')

# Plot monthly rates by phase vs time (hue by WellName)
fig_rate, axes_rate = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
for ax, phase in zip(axes_rate, phase_order):
	phase_df = rate_df[rate_df["phase"] == phase]
	sns.lineplot(
		data=phase_df,
		x="prod_date",
		y="monthly_rate",
		hue="WellName",
		marker="o",
		ax=ax,
		legend=False,
		color=phase_colors.get(phase),
	)
	ax.set_title(f"Monthly Production Rate - {phase}")
	ax.set_xlabel("Production Date")
	ax.set_ylabel("Monthly Rate")
fig_rate.tight_layout()

plt.show()
fig_rate.savefig(r'forecasting/plots/norm_monthly_rates.png')

