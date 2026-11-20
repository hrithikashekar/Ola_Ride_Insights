# Ola Ride Insights

An end-to-end analytics project on 103,024 Ola bookings in Bengaluru (July 2024): data cleaning, SQL analysis, a Power BI dashboard and a deployed Streamlit app.

**Live app:** https://olarideinsights-bs2ahqnxzuppa6mafdkfwr.streamlit.app/
## What the app shows

| Tab | What you get |
|---|---|
| **Dashboard** | Six KPI cards and five views that mirror the Power BI pages: Overall, Vehicle Type, Revenue, Cancellation, Ratings |
| **SQL insights** | 20 ready-made queries with their SQL code, result tables and CSV download, plus a read-only custom SQL box |
| **Data explorer** | Search by booking or customer ID, filter by payment method and location, download filtered data |
| **Power BI** | The published Power BI report embedded in the app |

Sidebar filters (date range, vehicle type, booking status) apply to the Dashboard and Data explorer tabs. The SQL tab always queries the full dataset.

## Key numbers

- 103,024 total bookings, 62.1% success rate
- About 35.1M in revenue from successful rides
- Seven vehicle types: Prime Sedan, Prime SUV, Prime Plus, Mini, Auto, Bike, E-Bike
- Four booking outcomes: Success, Canceled by Customer, Canceled by Driver, Driver Not Found

## Repository structure

```
.
├── app.py                          Streamlit app
├── requirements.txt                Python packages for deployment
├── .streamlit/
│   └── config.toml                 Theme settings
├── data/
│   ├── ola_cleaned.csv.gz          Cleaned dataset with derived features (read by the app)
│   ├── dim_vehicle.csv             Vehicle lookup table
│   ├── data_quality_report.txt     Cleaning and integrity log
│   └── OLA_DataSet.xlsx            Raw input data
└── sql/
    ├── 01_create_schema_mysql.sql  Table definition for MySQL
    ├── 02_ola_queries.sql          The 10 required business questions
    └── 03_dashboard_support_queries.sql   10 extra queries for the dashboard
```

The cleaning scripts, Power BI files (theme, DAX measures, build guide), EDA charts and insights deck are kept in the full local project and are not part of this repository.

## Run locally

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

The app opens at http://localhost:8501. The first KPI card should read 103,024 total bookings.

Use `python -m streamlit run app.py` if `streamlit` is not recognized on Windows.

## Use the SQL files in MySQL

1. Run `sql/01_create_schema_mysql.sql` to create the table. Enable `local_infile` if you want to load the CSV with `LOAD DATA`. The CSV must be extracted from `ola_cleaned.csv.gz` first.
2. Run `sql/02_ola_queries.sql` to answer the 10 required questions.
3. Run `sql/03_dashboard_support_queries.sql` for the extra queries used in the app.

Inside the app, the queries run on an in-memory SQLite copy of the same data, so no database setup is needed.

## Data notes

- `ola_cleaned.csv.gz` is compressed to stay under GitHub's 25 MB browser upload limit. Pandas reads it directly, so there is no need to unzip it.
- The raw Excel file and the cleaning log are included for reference. The app only needs the `.gz` file.

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub as a public repo.
2. Go to share.streamlit.io, click **Create app** and choose the repo, branch `main` and main file `app.py`.
3. Under **Advanced settings**, set Python to 3.11.
4. Click **Deploy**.

To show the Power BI report, publish it with **File, Embed report, Publish to web (public)**, then add the link in the app's **Settings, Secrets**:

```toml
POWERBI_EMBED_URL = "https://app.powerbi.com/view?r=YOUR_LINK_HERE"
```

## Tech stack

Python, pandas, Plotly, Streamlit, SQL (MySQL and SQLite), Power BI
