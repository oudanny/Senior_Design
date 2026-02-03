import pandas as pd
import numpy as np

df = pd.read_csv(r"C:\Users\txjam\Downloads\TF_Prod_Data.csv")
columns_to_convert = [
    'Norm. Cum. Water 3mo (bbl)', 'Norm. Cum. Water 6mo (bbl)',
    'Norm. Cum. Water 9mo (bbl)', 'Norm. Cum. Water 12mo (bbl)',
    'Norm. Cum. Water (bbl)', 'Norm. Cum. Oil 3mo (bbl)',
    'Norm. Cum. Gas 3mo (Mcf)', 'Norm. Cum Oil 6mo (bbl)',
    'Norm. Cum. Gas 6mo (Mcf)', 'Norm. Cum. Oil 9mo (bbl)',
    'Norm. Cum Gas 9mo (Mcf)', 'Norm. Cum Oil 12mo (bbl)',
    'Norm. Cum. Gas 12mo (Mcf)', 'Norm. Cum. Oil (bbl)',
    'Norm. Cum Gas (Mcf)'
]

df[columns_to_convert] = (
    df[columns_to_convert]
    .replace({',': ''}, regex=True)   # remove commas
    .apply(pd.to_numeric, errors='coerce')  # convert safely
)


import numpy as np

def quarterly_to_monthly(cum):
    """
    cum = array of cumulative volumes at 3,6,9,... months
    returns monthly volumes
    """
    cum = np.asarray(cum)
    Vq = np.diff(np.insert(cum,0,0))   # quarterly volumes

    monthly = []

    for i in range(len(Vq)):
        V = Vq[i]

        # estimate decline from next quarter
        if i < len(Vq)-1:
            R = Vq[i+1]/Vq[i]
            D = -np.log(R)/3
        else:
            D = -np.log(Vq[i]/Vq[i-1])/3  # repeat last decline

        q0 = V * D / (1 - np.exp(-3*D))

        # integrate each month
        for a,b in [(0,1),(1,2),(2,3)]:
            Vm = (q0/D)*(np.exp(-D*a)-np.exp(-D*b))
            monthly.append(Vm)

    return np.array(monthly)



def expand_normalized_to_monthly(df):
    """
    Expand normalized cumulative production (3,6,9,12 months)
    into estimated monthly production rows with:
        - ProdDate (actual calendar date)
    """

    monthly_rows = []

    for _, row in df.iterrows():

        # Parse production start date
        first_prod_date = pd.to_datetime(row["FirstProdDate"])

        # --- Cumulative checkpoints (normalized) ---
        cum = {
            3: {
                "oil":   row["Norm. Cum. Oil 3mo (bbl)"],
                "gas":   row["Norm. Cum. Gas 3mo (Mcf)"],
                "water": row["Norm. Cum. Water 3mo (bbl)"],
            },
            6: {
                "oil":   row["Norm. Cum Oil 6mo (bbl)"],
                "gas":   row["Norm. Cum. Gas 6mo (Mcf)"],
                "water": row["Norm. Cum. Water 6mo (bbl)"],
            },
            9: {
                "oil":   row["Norm. Cum. Oil 9mo (bbl)"],
                "gas":   row["Norm. Cum Gas 9mo (Mcf)"],
                "water": row["Norm. Cum. Water 9mo (bbl)"],
            },
            12: {
                "oil":   row["Norm. Cum Oil 12mo (bbl)"],
                "gas":   row["Norm. Cum. Gas 12mo (Mcf)"],
                "water": row["Norm. Cum. Water 12mo (bbl)"],
            }
        }

        checkpoints = [3, 6, 9, 12]
        prev_month = 0
        prev_vals = {"oil": 0, "gas": 0, "water": 0}

        # --- Build monthly rows ---
        for m in checkpoints:

            # Differences over the interval
            d_oil = cum[m]["oil"] - prev_vals["oil"]
            d_gas = cum[m]["gas"] - prev_vals["gas"]
            d_water = cum[m]["water"] - prev_vals["water"]

            months_in_block = m - prev_month

            avg_oil = d_oil / months_in_block
            avg_gas = d_gas / months_in_block
            avg_water = d_water / months_in_block

            for month in range(prev_month + 1, m + 1):

                # Actual production date
                prod_date = first_prod_date + pd.DateOffset(months=month - 1)

                monthly_rows.append({
                    **row.to_dict(),
                    "MonthNumber": month,
                    "ProdDate": prod_date,
                    "MonthlyOil_BBL": avg_oil,
                    "MonthlyGas_MCF": avg_gas,
                    "MonthlyWater_BBL": avg_water
                })

            prev_month = m
            prev_vals = cum[m]

    return pd.DataFrame(monthly_rows)



monthly_data = expand_normalized_to_monthly(df)
monthly_data.to_csv('ResEcon_MoProd.csv', index=False)