import pandas as pd

# -------------------------------------------------
# Load data
# -------------------------------------------------
df = pd.read_csv('./forecasting/wolfcamp_bupper_prod_norm.csv')

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

# -------------------------------------------------
# Wide → Long
# -------------------------------------------------
long_df = df.melt(
    id_vars=['WellName', 'FirstProdDate'],
    value_vars=columns_to_convert,
    var_name='metric',
    value_name='cum_prod'
)

long_df = long_df.dropna(subset=['cum_prod'])

long_df['cum_prod'] = (
    long_df['cum_prod']
    .astype(str)
    .str.replace(',', '', regex=False)
    .str.strip()
)

long_df['cum_prod'] = pd.to_numeric(long_df['cum_prod'], errors='coerce')
long_df = long_df.dropna(subset=['cum_prod'])

# -------------------------------------------------
# Extract phase + months
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

long_df = long_df[['WellName','FirstProdDate','phase','months','cum_prod']]

# -------------------------------------------------
# Add Month 0 cumulative = 0
# -------------------------------------------------
month0 = (
    long_df[['WellName','FirstProdDate','phase']]
    .drop_duplicates()
    .copy()
)

month0['months'] = 0
month0['cum_prod'] = 0

long_df = pd.concat([long_df, month0], ignore_index=True)

# -------------------------------------------------
# Compute production date
# -------------------------------------------------
long_df['prod_date'] = (
    long_df.apply(
        lambda row: row['FirstProdDate'] + pd.DateOffset(months=row['months']),
        axis=1
    )
)

long_df['prod_date'] = (
    long_df['prod_date']
    .dt.to_period('M')
    .dt.to_timestamp()
)

# -------------------------------------------------
# Expand to full monthly grid (0 → 12)
# -------------------------------------------------
def expand_monthly(group):

    # Get group keys safely (works in pandas 2.2+ / 3+)
    well_name, phase = group.name

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
    long_df
    .groupby(['WellName', 'phase'], group_keys=False)
    .apply(expand_monthly)
)

# -------------------------------------------------
# Linear interpolation (including Months 1–2)
# -------------------------------------------------
def interpolate_group(g):

    # recover group keys safely
    well_name, phase = g.name

    g = g.sort_values('prod_date').copy()

    g['cum_prod'] = g['cum_prod'].interpolate(method='linear')

    # restore identifiers
    g['WellName'] = well_name
    g['phase'] = phase

    return g

monthly = (
    monthly
    .groupby(['WellName','phase'], group_keys=False)
    .apply(interpolate_group)
)


# =================================================
# 1️⃣ WIDE MONTHLY CUMULATIVE (Month 0–12)
# =================================================
monthly_cum_wide = (
    monthly
    .pivot_table(
        index=['WellName', 'prod_date'],
        columns='phase',
        values='cum_prod'
    )
    .reset_index()
)

monthly_cum_wide.columns.name = None

monthly_cum_wide = monthly_cum_wide[
    ['WellName','prod_date','Oil','Gas','Water']
]

monthly_cum_wide[['Oil','Gas','Water']] = (
    monthly_cum_wide[['Oil','Gas','Water']]
    .fillna(0)
)

monthly_cum_wide.to_csv(
    './forecasting/monthly_cumulative_volumes.csv',
    index=False
)

# =================================================
# 2️⃣ WIDE MONTHLY RATES (Month 1–12)
# =================================================
monthly_rate = monthly.copy()

monthly_rate['monthly_rate'] = (
    monthly_rate
    .groupby(['WellName','phase'])['cum_prod']
    .diff()
)

monthly_rate = monthly_rate.dropna(subset=['monthly_rate'])

monthly_rate['monthly_rate'] = (
    monthly_rate['monthly_rate']
    .clip(lower=0)
)

monthly_rate_wide = (
    monthly_rate
    .pivot_table(
        index=['WellName','prod_date'],
        columns='phase',
        values='monthly_rate'
    )
    .reset_index()
)

monthly_rate_wide.columns.name = None

monthly_rate_wide = monthly_rate_wide.rename(columns={
    'Oil': 'Oil_rate',
    'Gas': 'Gas_rate',
    'Water': 'Water_rate'
})

monthly_rate_wide = monthly_rate_wide[
    ['WellName','prod_date','Oil_rate','Gas_rate','Water_rate']
]

monthly_rate_wide[['Oil_rate','Gas_rate','Water_rate']] = (
    monthly_rate_wide[['Oil_rate','Gas_rate','Water_rate']]
    .fillna(0)
)

monthly_rate_wide.to_csv(
    './forecasting/norm_monthly_rates.csv',
    index=False
)

print('✔ Wide cumulative (0–12) and wide monthly rates (1–12) written')
