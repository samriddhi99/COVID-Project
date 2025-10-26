# COVID Economic Dashboards Project

This repository contains interactive dashboards and a MySQL database for analyzing economic indicators during 2020–2023. It includes global and Europe-centric dashboards, with data stored in a relational MySQL database.

---

## Installing Dependencies

To run the dashboards and scripts, install the following Python packages:

~~~bash
pip install pandas mysql-connector-python dash plotly
~~~

> **Notes:**  
> - `mysql-connector-python` is required to connect to the MySQL database.  
> - `dash` and `plotly` are used for interactive dashboards.  
> - Make sure you have MySQL installed and running on your machine.

---

##  Running the Dashboards

### Global Dashboard
- **File:** `dashboard.py`  
- **Run:**
~~~bash
python3 dashboard.py
~~~
This dashboard shows global economic trends using the MySQL database.

### Europe-Centric Dashboards (in the europe folder)

1. **Unemployment Dashboard**
   - **File:** `unemployment_dashboard.py`  
   - **Run:**
   ~~~bash
   python3 unemployment_dashboard.py
   ~~~

2. **Inflation Dashboard**
   - **File:** `inflation.py`  
   - **Run:**
   ~~~bash
   python3 inflation_dashboard.py
   ~~~
   > **Important:** Before running, unzip the datasets folder and update the dataset path inside `inflation_dashboard.py` to match the unzipped location.

---

## MySQL Database

- **Database Name:** `economic_data`

- **Tables:**  
  1. `countries` — information about each country (`country_id`, `country_name`, `region`)  
  2. `indicators` — metadata about each economic indicator (`indicator_name`, `unit`, `description`)  
  3. `country_indicators` — yearly values of each indicator per country

- **Primary Keys:**  
  - `countries.country_id`  
  - `indicators.indicator_id`  
  - `country_indicators.record_id`

- **Foreign Keys:**  
  - `country_indicators.country_id → countries.country_id`  
  - `country_indicators.indicator_id → indicators.indicator_id`

- The database is stored in `economic_data.sql`.  
  To restore:
~~~bash
mysql -u root -p < economic_data.sql
~~~

- Connect to the database from Python using:
~~~python
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yourpassword",
    database="economic_data"
)
~~~
