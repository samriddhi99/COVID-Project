# 🌍 COVID-19 Economic Impact – European Data Dashboards

This repository explores the **economic and labour market impact of COVID-19 in Europe**, using official data from **Eurostat** and **Our World in Data**.  
It includes interactive dashboards built with **Python**, **Plotly Dash**, and **Bootstrap** for visualizing trends in **unemployment** and **inflation** across European countries.

---

## 📂 Project Structure

| File | Description |
|------|--------------|
| **Unemployment Analytics TSO .py** | Analytical script that processes Eurostat labour-market data (unemployment rate). Includes time-series computations and KPIs. |
| **Unemployment Dashboard.py** | Interactive **Dash app** visualizing monthly unemployment rates across EU countries. |
| **inflation dashboard.py** | Dash app visualizing **inflation trends (HICP)** across European countries from 2019 onward. Includes filtering by country and COICOP category. |
| **cleandata.py** | Data-cleaning script for Eurostat CSV exports. Handles date parsing, numeric conversion (comma decimals → dots), and filtering (e.g., keeping data from 2019+). |
| **dataset europe.zip** | Compressed folder containing the source Eurostat datasets used for analysis (unemployment, inflation, government measures, etc.). |

---

## 🧰 Requirements

Before running, install the dependencies:

```bash
pip install pandas plotly dash dash-bootstrap-components
