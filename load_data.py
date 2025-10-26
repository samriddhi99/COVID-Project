import pandas as pd
import mysql.connector

# --- Step 1: Read CSV ---
csv_path = "datasets/data_2020_2023.csv"
df = pd.read_csv(csv_path)

# --- Step 2: Connect to MySQL ---
conn = mysql.connector.connect(
    host="localhost",
    user="root",           # change if different
    password="abc123", # your password
    database="economic_data"
)
cursor = conn.cursor()

# --- Step 3: Insert countries (unique) ---
countries = df[['country_id', 'country_name']].drop_duplicates()

for _, row in countries.iterrows():
    cursor.execute("""
        INSERT IGNORE INTO countries (country_id, country_name)
        VALUES (%s, %s)
    """, (row['country_id'], row['country_name']))

conn.commit()

# --- Step 4: Prepare indicators list ---
indicators = [
    "Inflation (CPI %)",
    "GDP (Current USD)",
    "GDP per Capita (Current USD)",
    "Unemployment Rate (%)",
    "Interest Rate (Real, %)",
    "Inflation (GDP Deflator, %)",
    "GDP Growth (% Annual)",
    "Current Account Balance (% GDP)",
    "Government Expense (% of GDP)",
    "Government Revenue (% of GDP)",
    "Tax Revenue (% of GDP)",
    "Gross National Income (USD)",
    "Public Debt (% of GDP)"
]

# Insert indicators into the table
for name in indicators:
    cursor.execute("""
        INSERT IGNORE INTO indicators (indicator_name, unit)
        VALUES (%s, %s)
    """, (name, "%"))  # You can adjust units later
conn.commit()

# --- Step 5: Insert data into country_indicators ---
for _, row in df.iterrows():
    for name in indicators:
        # Get the indicator_id
        cursor.execute("SELECT indicator_id FROM indicators WHERE indicator_name = %s", (name,))
        indicator_id = cursor.fetchone()[0]

        value = row[name] if pd.notnull(row[name]) else None

        cursor.execute("""
            INSERT INTO country_indicators (country_id, indicator_id, year, value)
            VALUES (%s, %s, %s, %s)
        """, (row['country_id'], indicator_id, int(row['year']), value))

conn.commit()
cursor.close()
conn.close()

print("✅ Data successfully loaded into MySQL!")
