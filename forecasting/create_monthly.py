import pandas as pd

# -------------------------------------------------
# Load data
# -------------------------------------------------
df = pd.read_csv('./forecasting/normalized-TF-prod_csv.csv')

# Columns with quarterly cumulative data
columns_to_convert = [
    'Norm. Cum. Water 3mo (bbl)', 'Norm. Cum. Water 6mo (bbl)',
    'Norm. Cum. Water 9mo (bbl)', 'Norm. Cum. Water 12mo (bbl)',
    'Norm. Cum. Oil 3mo (bbl)',  'Norm. Cum. Gas 3mo (Mcf)', 
    'Norm. Cum Oil 6mo (bbl)',   'Norm. Cum. Gas 6mo (Mcf)', 
    'Norm. Cum. Oil 9mo (bbl)',  'Norm. Cum Gas 9mo (Mcf)', 
    'Norm. Cum Oil 12mo (bbl)',  'Norm. Cum. Gas 12mo (Mcf)',
]

df = df[['WellName', 'FirstProdDate'] + columns_to_convert]

# -------------------------------------------------
# Parse dates
# -------------------------------------------------
df['FirstProdDate'] = pd.to_datetime(df['FirstProdDate'])

# -------------------------------------------------
# Wide → Long (quarterly cumulative)
# -------------------------------------------------
long_df = df.melt(
    id_vars=['WellName', 'FirstProdDate'],
    value_vars=columns_to_convert,
    var_name='metric',
    value_name='cum_prod'
)

# Drop empty cumulative values
long_df = long_df.dropna(subset=['cum_prod'])

# Ensure cumulative production is numeric (strip commas/spaces)
long_df['cum_prod'] = (
    long_df['cum_prod']
    .astype(str)
    .str.replace(',', '', regex=False)
    .str.strip()
)
long_df['cum_prod'] = pd.to_numeric(long_df['cum_prod'], errors='coerce')
long_df = long_df.dropna(subset=['cum_prod'])

# -------------------------------------------------
# Extract phase and months from column names
# -------------------------------------------------
long_df['phase'] = (
    long_df['metric']
    .str.extract(r'Cum\.?\s*(Oil|Gas|Water)', expand=False)
)

long_df['months'] = (
    long_df['metric']
    .str.extract(r'(\d+)mo', expand=False)
    .astype(int)
)

# -------------------------------------------------
# Compute production date from FirstProdDate
# -------------------------------------------------
long_df['prod_date'] = (
    long_df.apply(
        lambda row: row['FirstProdDate'] + pd.DateOffset(months=row['months']),
        axis=1
    )
)

# -------------------------------------------------
# Keep clean quarterly cumulative table
# -------------------------------------------------
final_df = (
    long_df[['WellName', 'phase', 'prod_date', 'cum_prod']]
    .sort_values(['WellName', 'phase', 'prod_date'])
    .reset_index(drop=True)
)

# Align to month start
final_df['prod_date'] = (
    final_df['prod_date']
    .dt.to_period('M')
    .dt.to_timestamp()
)

# -------------------------------------------------
# Expand to monthly grid per well + phase
# -------------------------------------------------
def expand_monthly(group):
    # Pandas 3+ may exclude group keys from the group frame
    well_name = None
    phase = None
    if isinstance(group.name, tuple):
        well_name, phase = group.name
    else:
        well_name = group.name

    if 'WellName' in group.columns:
        well_name = group['WellName'].iloc[0]
    if 'phase' in group.columns:
        phase = group['phase'].iloc[0]
    
    idx = pd.date_range(
        start=group['prod_date'].min(),
        end=group['prod_date'].max(),
        freq='MS'
    )

    out = (
        group
        .set_index('prod_date')
        .reindex(idx)
        .rename_axis('prod_date')
        .reset_index()
    )

    # Reattach identifiers
    out['WellName'] = well_name
    out['phase'] = phase

    return out


monthly = (
    final_df
    .groupby(['WellName', 'phase'], group_keys=False)
    .apply(expand_monthly)
)

# -------------------------------------------------
# Interpolate monthly cumulative volumes
# -------------------------------------------------
monthly['cum_prod'] = (
    monthly
    .groupby(['WellName', 'phase'])['cum_prod']
    .transform(lambda s: s.interpolate(method='linear'))
)

monthly = monthly.dropna(subset=['cum_prod'])

# -------------------------------------------------
# Save monthly cumulative volumes
# -------------------------------------------------
monthly_cum = monthly[['WellName', 'phase', 'prod_date', 'cum_prod']]

monthly_cum.to_csv(
    './forecasting/monthly_cumulative_volumes.csv',
    index=False
)

# -------------------------------------------------
# Convert cumulative → monthly rates
# -------------------------------------------------
monthly_rate = monthly.copy()

monthly_rate['monthly_rate'] = (
    monthly_rate
    .groupby(['WellName', 'phase'])['cum_prod']
    .diff()
)

monthly_rate = monthly_rate.dropna(subset=['monthly_rate'])

# Enforce non-negative rates
monthly_rate['monthly_rate'] = monthly_rate['monthly_rate'].clip(lower=0)

# -------------------------------------------------
# Save monthly rates
# -------------------------------------------------
monthly_rate_df = monthly_rate[
    ['WellName', 'phase', 'prod_date', 'monthly_rate']
]

monthly_rate_df.to_csv(
    './forecasting/norm_monthly_rates.csv',
    index=False
)

print('✔ Monthly cumulative and rate CSVs written')

