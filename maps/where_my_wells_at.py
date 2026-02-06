import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('/workspaces/Senior_Design/forecasting/normalized-TF-prod_csv.csv')
df.dropna(subset=['Latitude', 'Longitude'], inplace=True)

# --- Local projection (lat/lon → meters) ---
lat = df["Latitude"].to_numpy()
lon = df["Longitude"].to_numpy()

lat0 = np.deg2rad(lat.mean())
R = 6_371_000  # Earth radius (m)

df["x_m"] = np.deg2rad(lon - lon.mean()) * R * np.cos(lat0)
df["y_m"] = np.deg2rad(lat - lat.mean()) * R

# --- First plot: original local coordinates ---
fig, ax = plt.subplots(figsize=(10, 10))

sns.scatterplot(
    data=df,
    x="x_m",
    y="y_m",
    hue="ENVInterval",
    ax=ax
)

ax.set_title("Well Locations by ENV Interval")
ax.set_xlabel("Meters East")
ax.set_ylabel("Meters North")
ax.set_aspect("equal", adjustable="box")
ax.legend(title="ENV Interval")

plt.show()


# --- PCA-based rotation to align main axis with x-axis ---
coords = df[['x_m', 'y_m']].to_numpy()
coords_centered = coords - coords.mean(axis=0)

cov = np.cov(coords_centered, rowvar=False)
eigenvalues, eigenvectors = np.linalg.eigh(cov)
principal_vector = eigenvectors[:, np.argmax(eigenvalues)]
angle = np.arctan2(principal_vector[1], principal_vector[0])
print(f"Rotation angle (degrees): {np.degrees(angle):.2f}")

c, s = np.cos(-angle), np.sin(-angle)
R_mat = np.array([[c, -s],
                  [s,  c]])

rotated_coords = coords_centered @ R_mat.T
df['x_rot'] = rotated_coords[:, 0]
df['y_rot'] = rotated_coords[:, 1]

# --- Second plot: rotated coordinates ---
fig2, ax2 = plt.subplots(figsize=(10, 6))

sns.scatterplot(data=df, x='x_rot', y='y_rot', hue='ENVInterval', ax=ax2, s=80)

ax2.set_title('Well Locations Rotated to Align with X-axis')
ax2.set_xlabel('Rotated X (meters)')
ax2.set_ylabel('Rotated Y (meters)')
ax2.axhline(0, color='gray', linestyle='--', alpha=0.7)
# ax2.set_aspect('equal', adjustable='box')
ax2.set_ylim(-100,100)
ax2.legend(title='ENV Interval')

plt.show()

df_wolfcampb = df[df['ENVInterval'] == 'WOLFCAMP B UPPER']
df_wolfcampb = df_wolfcampb.sort_values('x_rot')
print(df_wolfcampb[['WellName', 'x_rot']])