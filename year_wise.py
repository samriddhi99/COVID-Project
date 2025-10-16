import pandas as pd

# Read the dataset
df = pd.read_csv("datasets/WHO-COVID-19-global-daily-data.csv")

# Convert date column to datetime
df["Date_reported"] = pd.to_datetime(df["Date_reported"])

# Extract year
df["Year"] = df["Date_reported"].dt.year

# Replace missing values with 0
df["New_cases"] = df["New_cases"].fillna(0)
df["New_deaths"] = df["New_deaths"].fillna(0)

# Group by country and year, summing up cases and deaths
summary = (
    df.groupby(["Country", "Year"], as_index=False)[["New_cases", "New_deaths"]]
    .sum()
    .rename(columns={"New_cases": "Total_cases", "New_deaths": "Total_deaths"})
)

# Save or display
print(summary.head())
summary.to_csv("country_yearly_covid_summary.csv", index=False)
