# 🏏 IPL Analytics Pro (2008–2026)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Framework-Streamlit%201.63-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Visualization-Plotly%20Express-00C9FF.svg)](https://plotly.com/)
[![Tests](https://img.shields.io/badge/Tests-10%2F10%20Passing-brightgreen.svg)](https://pytest.org/)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/Data%20License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

**IPL Analytics Pro** is an enterprise-grade cricket analytics and interactive intelligence platform delivering audit-grade historical insights from all 19 editions of the Indian Premier League (**2008 through 2026**).

Built on official ball-by-ball records from **[Cricsheet](https://cricsheet.org/)**, the system strictly forbids fabricated data, enforces ICC cricket scoring laws (including extra attribution under Law 21), isolates non-regulation play (Super Overs), and provides an interactive Plotly-powered Streamlit web application protected by secure `bcrypt` authentication.

---

## 📌 Key Highlights

- **19 Complete Seasons (2008–2026):** 1,243 verified matches, 295,732 ball-by-ball deliveries, 398,965 runs, and 15,287 wickets.
- **Verified 2026 Coverage:** All 74 matches of the 2026 season (March 28 to May 31, 2026) verified and integrated.
- **ICC Law 21 Compliance:** Bowler runs conceded strictly exclude byes and leg-byes; bowler wickets exclude run-outs.
- **Interactive Plotly Visualizations:** 20+ responsive charts with customized dark sports aesthetics, hover tooltips, and zero clashing colors.
- **Modular Statistical Engines:** Independent, reusable Python classes for Season, Team, Player, Venue, and Match analytics.
- **Production-Ready Authentication:** SQLite user management, salt-hashed passwords via `bcrypt` (12 rounds), input validation, and route guards.
- **Automated QA Pipeline:** 10 automated unit and regression tests passing with 100% success.

---

## 🛠️ Technology Stack

| Domain | Technology | Purpose |
|:---|:---|:---|
| **Language** | Python 3.10 – 3.12 | Core data processing and application logic |
| **Data Engine** | Pandas 3.0+ & NumPy 2.5+ | Relational joins, extra calculations, aggregations |
| **High-Performance Storage** | Apache Parquet (PyArrow) | Sub-second ball-by-ball queries across 300,000+ records |
| **Visualizations** | Plotly Express & Plotly Graph Objects | Interactive, responsive dark-themed charts |
| **Supplementary Analytics** | Matplotlib & Seaborn | Static exploratory reports and notebook generation |
| **Application UI** | Streamlit 1.63+ (Multi-Page App) | Reactive web dashboard with custom CSS glassmorphism |
| **Security & Auth** | SQLite 3 & `bcrypt` | Salt-hashed credentials and session management |
| **Testing** | `pytest` | Unit, relational, and regression test suites |

---

## 📁 Repository Structure

```text
ipl-analytics-pro/
├── app.py                      # Main entry portal & Overview Dashboard
├── pages/
│   ├── 1_Season_Analysis.py    # Longitudinal trends & season points tables
│   ├── 2_Team_Analysis.py      # Franchise rankings & Head-to-Head simulator
│   ├── 3_Player_Analysis.py    # Batting & bowling leaders, batter vs bowler, Kohli deep dive
│   ├── 4_Venue_Analysis.py     # Stadium usage, par scores & chasing bias
│   ├── 5_Match_Insights.py     # Record totals, closest finishes, highest individual scores
│   ├── 6_Data_Quality.py       # Data provenance, validation checklist, coverage table
│   └── 7_About.py              # Architecture, tech stack & project philosophy
├── analytics/                  # Reusable statistical engines
│   ├── __init__.py
│   ├── data_loader.py          # Cached data loading utility
│   ├── season_analysis.py      # SeasonAnalytics class
│   ├── team_analysis.py        # TeamAnalytics class
│   ├── player_analysis.py      # PlayerAnalytics class
│   ├── venue_analysis.py       # VenueAnalytics class
│   └── match_insights.py       # MatchInsights class
├── auth/                       # Secure authentication system
│   ├── __init__.py
│   ├── database.py             # SQLite database manager
│   └── authentication.py       # bcrypt hashing & session management
├── components/                 # Reusable Streamlit UI components
│   ├── __init__.py
│   ├── sidebar.py              # Branded navigation & user badge
│   ├── kpi_cards.py            # Glassmorphic KPI cards
│   ├── charts.py               # Plotly chart generators
│   └── filters.py              # Global synchronized filter bar
├── data/
│   ├── raw/                    # Immutable raw Cricsheet data & manifest
│   │   ├── data_manifest.json
│   │   └── ipl_csv2.zip
│   └── processed/              # Cleaned datasets
│       ├── matches_cleaned.csv
│       ├── deliveries_cleaned.parquet
│       └── deliveries_cleaned.csv
├── scripts/                    # Automated reproducible data pipelines
│   ├── download_data.py        # Automated Cricsheet downloader & extractor
│   ├── clean_data.py           # Cleaning, extra resolution & standardization
│   ├── validate_data.py        # Comprehensive integrity audit script
│   └── run_eda.py              # Exploratory charting & notebook builder
├── notebooks/                  # Reproducible Jupyter exploratory notebooks
│   ├── 01_data_exploration.ipynb
│   └── 02_ipl_analysis.ipynb
├── reports/                    # Audit reports and generated charts
│   ├── dataset_acquisition_report.md
│   ├── data_quality_report.md
│   ├── eda_summary.md
│   └── charts/                 # 10 High-res static PNG figures
├── tests/                      # Automated Pytest suite
│   ├── test_cleaning.py        # Data structure & cricket rules tests
│   ├── test_analytics.py       # Statistical engine calculation tests
│   └── test_authentication.py  # bcrypt & login security tests
├── assets/
│   └── style.css               # Modern dark sports analytics design system
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git exclusion rules
├── .env.example                # Environment variables template
└── README.md                   # Project documentation
```

---

## ⚡ Quickstart & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ipl-analytics-pro.git
cd ipl-analytics-pro
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Reproduce Data Pipeline (Optional — Processed Data Included)
```bash
# 1. Download raw data from Cricsheet
python scripts/download_data.py

# 2. Clean, standardize, and process datasets
python scripts/clean_data.py

# 3. Run validation assertions
python scripts/validate_data.py

# 4. Generate EDA charts and notebooks
python scripts/run_eda.py
```

### 5. Launch the Streamlit Web Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🔐 Authentication & Demo Account

The application features a secure user account and access control system.

| Role | Username | Password | Access Level |
|:---|:---:|:---:|:---:|
| **Lead Analyst (Pre-seeded Demo)** | `demo` | `IPL@Analytics2026` | Full Dashboard Access |

- Passwords are salt-hashed using **bcrypt with 12 rounds**.
- Users can also create new accounts directly from the **Create Account** tab with duplicate username/email prevention.
- The login screen includes a **"Quick Fill Demo Credentials"** button for immediate evaluation.

---

## 🧪 Running Automated Tests

Run the complete Pytest verification suite across data cleaning, statistical modules, and authentication:

```bash
python -m pytest tests/ -v
```

**Test Coverage Summary:**
- `test_cleaning.py`: Validates match uniqueness, delivery count, extras summation logic, and bowler runs conceded.
- `test_analytics.py`: Validates Season, Team, Player, Venue, and Match statistical outputs across all 19 seasons.
- `test_authentication.py`: Validates bcrypt hashing, password checking, input validation, and account authentication.

---

## 📊 Data Coverage & Provenance (2008–2026)

| Season | Verified Matches | Total Deliveries | Total Runs | Fours (4s) | Sixes (6s) | Wickets |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **2008** | 58 | 13,489 | 17,937 | 1,709 | 623 | 684 |
| **2009** | 57 | 13,607 | 16,088 | 1,321 | 506 | 741 |
| **2010** | 60 | 14,488 | 18,864 | 1,709 | 585 | 827 |
| **2011** | 73 | 17,278 | 21,154 | 1,916 | 639 | 873 |
| **2012** | 74 | 17,732 | 22,453 | 1,911 | 731 | 860 |
| **2013** | 76 | 18,177 | 22,541 | 2,052 | 681 | 911 |
| **2014** | 60 | 14,331 | 18,909 | 1,561 | 714 | 743 |
| **2015** | 59 | 13,658 | 18,332 | 1,609 | 692 | 689 |
| **2016** | 60 | 14,096 | 18,862 | 1,633 | 638 | 695 |
| **2017** | 59 | 13,861 | 18,769 | 1,611 | 705 | 746 |
| **2018** | 60 | 14,345 | 20,706 | 1,652 | 872 | 739 |
| **2019** | 60 | 14,293 | 19,400 | 1,653 | 778 | 766 |
| **2020** | 60 | 14,525 | 19,352 | 1,624 | 734 | 771 |
| **2021** | 60 | 14,142 | 18,648 | 1,556 | 675 | 734 |
| **2022** | 74 | 17,912 | 24,395 | 2,017 | 1,062 | 938 |
| **2023** | 74 | 17,863 | 25,688 | 2,174 | 1,124 | 916 |
| **2024** | 71 | 17,143 | 25,972 | 2,137 | 1,260 | 857 |
| **2025** | 74 | 17,665 | 25,841 | 2,148 | 1,245 | 895 |
| **2026** | 74 | 17,828 | 26,054 | 2,165 | 1,288 | 902 |
| **Total** | **1,243** | **295,732** | **398,965** | **34,107** | **15,286** | **15,287** |

---

## 🚀 GitHub Upload Instructions

To upload this project to your GitHub account:

```bash
# 1. Initialize git repository
git init

# 2. Stage all project files (.gitignore protects credentials and cache)
git add .

# 3. Create initial GitHub commit
git commit -m "feat: complete IPL Analytics Pro platform (2008-2026)"

# 4. Set main branch
git branch -M main

# 5. Link to your GitHub repository
git remote add origin https://github.com/<your-username>/ipl-analytics-pro.git

# 6. Push code to GitHub
git push -u origin main
```

---

## 📜 License & Attribution

- **Data Attribution:** Cricket data provided by **[Cricsheet](https://cricsheet.org/)**, licensed under **[Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/)**.
- **Code License:** MIT License. Free for educational and personal use.
