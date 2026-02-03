import pandas as pd
import numpy as np

df = pd.read_excel(r"C:\Users\txjam\Documents\homework\design\forecasting\normalized-TF-prod.xlsx",skiprows=1,usecols="B:AN")
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




import numpy as np

def arps_quarter_to_monthly(cum, b=0.8, well_id="UNKNOWN"):
    cum = np.asarray(cum, dtype=float)
    Vq = np.diff(np.insert(cum, 0, 0))

    print("\n==============================")
    print("WELL:", well_id)
    print("CUM:", cum)
    print("Vq :", Vq)

    monthly = []

    for i in range(len(Vq)):

        V = Vq[i]

        # ----- ratio -----
        if i < len(Vq)-1 and Vq[i] > 0:
            R = Vq[i+1]/Vq[i]
        elif i > 0 and Vq[i-1] > 0:
            R = Vq[i]/Vq[i-1]
        else:
            R = 1.0

        print(f"\nQuarter {i}: V={V:.2f}, R={R:.4f}")

        # ============================
        # Flat / ramp
        # ============================
        if R > 0.98:
            print(" → FLAT (ramp/plateau)")
            monthly.extend([V/3]*3)
            continue

        # ============================
        # Exponential
        # ============================
        if R > 0.85:
            print(" → EXPONENTIAL")
            D = -np.log(max(R,1e-6))/3
            print("   D =",D)

            q0 = V*D/(1-np.exp(-3*D))
            for a,bm in [(0,1),(1,2),(2,3)]:
                Vm = (q0/D)*(np.exp(-D*a)-np.exp(-D*bm))
                monthly.append(Vm)
            continue

        # ============================
        # Hyperbolic
        # ============================
        print(" → HYPERBOLIC")

        def ratio(D):
            if 1 + b*D*6 <= 0:
                return 1e6
            num = (1 + b*D*3)**((b-1)/b) - (1 + b*D*6)**((b-1)/b)
            den = 1 - (1 + b*D*3)**((b-1)/b)
            return num/den - R

        D = -np.log(max(R,1e-6))/3
        print("   Initial D =",D)

        for n in range(15):
            f = ratio(D)
            dD = 1e-5
            df = (ratio(D+dD) - f)/dD

            if abs(df) < 1e-10:
                print("   Newton stalled")
                break

            D -= f/df

            # enforce domain
            if 1 + b*D*6 <= 0:
                D = -0.99/(b*6)

            print(f"   iter {n}: D={D:.6f}, 1+bDt(6)={1+b*D*6:.6f}")

        # compute qi
        base = 1 + b*D*3
        if base <= 0:
            print("   ⚠️  INVALID Arps domain → falling back to exponential")
            D = -np.log(R)/3
            q0 = V*D/(1-np.exp(-3*D))
            for a,bm in [(0,1),(1,2),(2,3)]:
                Vm = (q0/D)*(np.exp(-D*a)-np.exp(-D*bm))
                monthly.append(Vm)
            continue

        qi = V*(1-b)*D / (1 - base**((b-1)/b))

        for a,bm in [(0,1),(1,2),(2,3)]:
            Vm = (qi/((1-b)*D))*(
                (1+b*D*a)**((b-1)/b) -
                (1+b*D*bm)**((b-1)/b)
            )
            monthly.append(Vm)

    return np.array(monthly)




def expand_normalized_to_monthly(df, b=0.8):

    monthly_rows = []

    for _, row in df.iterrows():

        first_prod = pd.to_datetime(row["FirstProdDate"])

        oil_cum   = [row["Norm. Cum. Oil 3mo (bbl)"],
                     row["Norm. Cum Oil 6mo (bbl)"],
                     row["Norm. Cum. Oil 9mo (bbl)"],
                     row["Norm. Cum Oil 12mo (bbl)"]]

        gas_cum   = [row["Norm. Cum. Gas 3mo (Mcf)"],
                     row["Norm. Cum. Gas 6mo (Mcf)"],
                     row["Norm. Cum Gas 9mo (Mcf)"],
                     row["Norm. Cum. Gas 12mo (Mcf)"]]

        water_cum = [row["Norm. Cum. Water 3mo (bbl)"],
                     row["Norm. Cum. Water 6mo (bbl)"],
                     row["Norm. Cum. Water 9mo (bbl)"],
                     row["Norm. Cum. Water 12mo (bbl)"]]
        try:
            oil_m   = arps_quarter_to_monthly(oil_cum, b,well_id=row.get("WellName","UNKNOWN"))
        except Exception as e:
            print("FAILED WELL:")
            print(row[[
            "Norm. Cum. Oil 3mo (bbl)",
            "Norm. Cum Oil 6mo (bbl)",
            "Norm. Cum. Oil 9mo (bbl)",
            "Norm. Cum Oil 12mo (bbl)"
            ]])
            raise e
        gas_m   = arps_quarter_to_monthly(gas_cum, b)
        water_m = arps_quarter_to_monthly(water_cum, b)

        for i in range(12):
            monthly_rows.append({
                **row.to_dict(),
                "MonthNumber": i+1,
                "ProdDate": first_prod + pd.DateOffset(months=i),
                "MonthlyOil_BBL": oil_m[i],
                "MonthlyGas_MCF": gas_m[i],
                "MonthlyWater_BBL": water_m[i]
            })

    return pd.DataFrame(monthly_rows)



#%%
if __name__ == "__main__":
    df[columns_to_convert] = (
    df[columns_to_convert]
    .replace({',': ''}, regex=True)   # remove commas
    .apply(pd.to_numeric, errors='coerce')  # convert safely
    )
    df.dropna(inplace=True)

    monthly_data = expand_normalized_to_monthly(df)
    monthly_data.dropna(inplace=True)
    monthly_data.to_csv(r'C:\Users\txjam\Documents\homework\design\forecasting\ResEcon_MoProd.csv', index=False)
    # print(df.head())