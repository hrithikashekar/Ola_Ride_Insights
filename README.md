# Ola Ride Insights

End-to-end analytics project: data cleaning → SQL → Power BI → Streamlit → business insights (July 2024, 103,024 Ola bookings in Bengaluru).

```
ola_ride_insights/
├── app.py                         Streamlit app (Dashboard · SQL Insights · Data Explorer · Power BI embed)
├── requirements.txt, .streamlit/  Deployment config
├── data/
│   ├── OLA_DataSet.xlsx           Raw input
│   ├── ola_cleaned.csv            Cleaned + 17 derived features (used by SQL, app, Power BI)
│   ├── dim_vehicle.csv            Vehicle icon lookup
│   └── data_quality_report.txt    Cleaning/integrity log
├── scripts/
│   ├── 01_clean_and_eda.py        Cleaning, preprocessing, EDA charts
│   └── 03_build_insights_deck.py  Fills Ola-Slides.pptx with insights
├── sql/
│   ├── 01_create_schema_mysql.sql Table DDL + LOAD DATA
│   ├── 02_ola_queries.sql         The 10 required questions
│   └── 03_dashboard_support_queries.sql  10 extra BI queries
├── powerbi/                       Power Query M, DAX measures, theme, build guide
├── eda_charts/                    EDA PNGs
└── docs/
    ├── Ola_Ride_Insights_Deck.pptx  Insights deck built on your template
    ├── Ola-Slides.pptx              Original template
    └── PROJECT_DOCUMENTATION.md
```

## Run
```bash
pip install -r requirements.txt pandas openpyxl matplotlib seaborn python-pptx
python scripts/01_clean_and_eda.py          # regenerates data/ + eda_charts/
streamlit run app.py
```
MySQL: run `sql/01_create_schema_mysql.sql` (enable `local_infile`), then `02_ola_queries.sql`.

## Deploy (Streamlit Community Cloud)
Push this folder to GitHub (`git init && git add . && git commit -m "Ola ride insights"`), then share.streamlit.io → New app → select repo, main file `app.py`. `data/ola_cleaned.csv` (~30 MB) must be in the repo (under GitHub's 100 MB limit). Add `POWERBI_EMBED_URL` under *Secrets* if you publish the report.
