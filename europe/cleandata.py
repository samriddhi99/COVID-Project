import pandas as pd
from pathlib import Path


csv_path = Path("prc_hicp_manr_linear.csv")

df = pd.read_csv(csv_path)


df.columns = (
    df.columns.str.strip()
              .str.replace(r"\s+", "_", regex=True)
              .str.lower()
)

# --- parse date ---
# TIME_PERIOD contains e.g. "2019-12" or "2020-01"
df["time"] = pd.to_datetime(df["time_period"], errors="coerce")


df["obs_value"] = (
    df["obs_value"]
      .astype(str)
      .str.replace(",", ".", regex=False)
      .astype(float)
)


df_filtered = df[df["time"] >= "2019-01-01"].copy()


keep_cols = ["geo", "time", "obs_value", "unit", "coicop"]
df_filtered = df_filtered[keep_cols]

# --- save cleaned file ---
out_path = csv_path.with_name("prc_hicp_manr_cleaned.csv")
df_filtered.to_csv(out_path, index=False)

print(f"Cleaned data saved to: {out_path}")
print(df_filtered.head())
