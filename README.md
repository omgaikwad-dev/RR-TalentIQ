# 🏏 IPL Analytics Pro & 👑 RR TalentIQ (2008–2027)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Framework-Streamlit%201.65-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Visualization-Plotly%207.1-00C9FF.svg)](https://plotly.com/)
[![Tests](https://img.shields.io/badge/Tests-41%2F41%20Passing-brightgreen.svg)](https://pytest.org/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn%201.9-F7931E.svg)](https://scikit-learn.org/)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/Data%20License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

**RR TalentIQ** is an advanced domestic cricket talent scouting and IPL 2027 auction intelligence platform integrated directly into **IPL Analytics Pro (2008–2026)**.

The platform was engineered to power an individual submission for the **Rajasthan Royals SupeRR Selector Season 2** competition. Its Round 1 objective is to identify, evaluate, and justify the **Top 10 youngest uncapped domestic cricket talents** that Rajasthan Royals should back at the upcoming **IPL 2027 Auction**.

---

## 📌 Platform Dual Architecture

| Capability | Module Namespace | Primary Focus |
|:---|:---|:---|
| **IPL Analytics Pro** | `analytics/`, `pages/1-7` | 19 seasons of historical IPL match records (1,243 matches, 295,732 deliveries) |
| **RR TalentIQ Scouting** | `scouting/`, `pages/8-14` | Uncapped domestic talent scouting, age reference auditing, potential curve modeling, MCDA ranking |
| **Machine Learning Intelligence** | `ml/`, `pages/15` | Unsupervised K-Means clustering, PCA latent projections, z-score feature attribution |
| **RR Auction Strategy** | `auction/`, `pages/16` | RR squad depth audit, priority gaps, estimated market valuation, 4-quadrant budget optimization |
| **Strategy Reporting Engine** | `reports/`, `pages/17` | Publication-grade PDF Strategy Dossier (`reportlab`) & automated 16-Slide PPTX Deck (`python-pptx`) |

---

## 🛠️ Complete Repository Architecture

```text
ipl-analytics-pro/ (branch: feature/rr-talentiq)
├── app.py                          # Unified portal & historical IPL overview
├── pages/                          # Multipage application (17 verified pages)
│   # --- Historical IPL Intelligence ---
│   ├── 1_Season_Analysis.py        # Longitudinal season standings & scoring rates
│   ├── 2_Team_Analysis.py          # Franchise rankings & head-to-head matrix
│   ├── 3_Player_Analysis.py        # Career batting/bowling records & Kohli analysis
│   ├── 4_Venue_Analysis.py         # Ground par scores & toss chasing bias
│   ├── 5_Match_Insights.py         # Record team totals & closest finishes
│   ├── 6_Data_Quality.py           # ICC Law 21 compliance & relational audit
│   ├── 7_About.py                  # Architecture, tech stack & project philosophy
│   # --- RR TalentIQ Domestic Scouting & Auction ---
│   ├── 8_Scouting_Overview.py      # Mission control, KPI cards, role/age distributions
│   ├── 9_Player_Explorer.py        # 360° talent dossiers, 7-axis radar, CSV export
│   ├── 10_Batting_Scouting.py      # Batting Impact Index (BII), strike efficiency frontier
│   ├── 11_Bowling_Scouting.py      # Bowling Impact Index (BII), economy containment
│   ├── 12_All_Rounder_Analysis.py  # Harmonic dual-discipline gating & wicketkeeper index
│   ├── 13_Player_Comparison.py     # Head-to-head comparison for up to 4 candidates
│   ├── 14_Talent_Rankings.py       # Live MCDA weight calibration & sensitivity analysis
│   ├── 15_ML_Intelligence.py       # K-Means archetypes, 2D PCA latent map, explainability
│   ├── 16_Auction_Strategy.py      # 4-Quadrant Value vs Cost matrix & RR squad gap audit
│   └── 17_Scouting_Reports.py      # One-click downloadable PDF dossier & PPTX slide deck
├── analytics/                      # Analytical and mathematical engines
│   ├── domestic_data_loader.py     # Adaptive CSV/Excel ingestion, synonym mapper, 10-pt QA audit
│   ├── batting_scouting.py         # Batting metrics, boundary ball %, non-linear confidence
│   ├── bowling_scouting.py         # Bowling metrics, decimal overs, dot ball pressure
│   ├── allrounder_scouting.py      # Independent 2-way evaluation & keeper glovework metrics
│   ├── consistency_analysis.py     # Innings volatility, conversion rates, sample reliability
│   └── performance_normalization.py# Percentile & Min-Max normalization to [0, 100] scale
├── scouting/                       # Scouting decision logic
│   ├── age_eligibility.py          # Reference date (2027-01-01) age calculator & cap audit
│   ├── uncapped_filter.py          # Uncapped domestic pool filter & exclusions tracker
│   ├── role_classifier.py          # Empirical role & tactical archetype inference
│   ├── potential_score.py          # Age curve modeling & development headroom ceiling
│   ├── player_ranker.py            # Multi-criteria decision ranker & sensitivity engine
│   ├── player_profiles.py          # 360° dossier compiler with automated strengths/weaknesses
│   └── recommendations.py          # Top 10 Youngest Uncapped Recommendation Engine
├── ml/                             # Scikit-learn machine learning suite
│   ├── preprocessing.py            # Feature engineering, median imputer, StandardScaler
│   ├── clustering.py               # K-Means clustering with silhouette score validation
│   ├── player_model.py             # PCA dimensionality reduction (2D coordinates)
│   └── explainability.py           # Z-score cohort attribution (positive/negative drivers)
├── auction/                        # Franchise auction intelligence
│   ├── rr_squad_analysis.py        # Verified RR core squad & 7-department depth audit
│   ├── squad_requirements.py       # 5-tier scouting priority matrix & squad fit scoring
│   ├── player_valuation.py         # Base price, role scarcity factors, max bid ceilings
│   └── auction_strategy.py         # Value vs Cost quadrants & ₹14.0 Cr auction cart optimizer
├── reports/                        # Deliverables compilation
│   ├── executive_summary.py        # Publication-grade ReportLab PDF generator
│   └── presentation_export.py      # Automated 16-Slide python-pptx presentation deck generator
├── tests/                          # Automated Pytest suite (41/41 passing)
│   ├── test_analytics.py           # Historical IPL analytics unit tests
│   ├── test_authentication.py      # bcrypt authentication & SQLite user tests
│   ├── test_cleaning.py            # Cricsheet data cleaning rules & extra validations
│   ├── test_domestic_data.py       # Domestic ingestion, adaptive synonyms, QA report tests
│   ├── test_eligibility.py         # Age reference date, capped player exclusion tests
│   ├── test_batting_metrics.py     # Batting impact index, rotation SR, sample confidence tests
│   ├── test_bowling_metrics.py     # Bowling impact index, decimal overs, harmonic gating tests
│   ├── test_player_ranking.py      # Leaderboard, potential curves, sensitivity tests
│   ├── test_ml.py                  # K-Means, silhouette score, PCA, explainability tests
│   ├── test_auction.py             # RR squad depth, valuation math, auction quadrant tests
│   └── test_reports.py             # PDF & PPTX file generation tests
├── data/
│   ├── raw/                        # Cricsheet archive & RR competition drop folder
│   ├── processed/                  # Cleaned parquet & CSV datasets
│   └── sample/                     # Synthetic test fixtures explicitly isolated for QA
├── assets/style.css                # Dark sports design system (Rajasthan Royals palette)
└── requirements.txt                # Complete project dependencies

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

### 4. Run the Automated Test Suite (41 Tests)
```bash
python -m pytest tests/ -v
```
All 41 unit and regression tests will execute across both historical IPL and domestic scouting modules.

### 5. Launch the Streamlit Web Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📥 Domestic Data Ingestion & Competition Pack Guide

The platform includes an adaptive ingestion pipeline ([`analytics/domestic_data_loader.py`](file:///d:/RR/ipl-analytics-pro/analytics/domestic_data_loader.py)) ready to accept the official **Rajasthan Royals SupeRR Selector competition pack**:

1. Place your competition files (CSV, Excel `.xlsx`/`.xls`, Parquet, or JSON) directly into:
   ```text
   data/raw/rr_competition/
   ```
2. The system automatically scans the folder, adaptively maps columns (matching synonyms like `bf`, `balls_faced`, `ov`, `rc`, `wkts`), validates cricket mathematics (Strike Rate, Economy, Boundary %), and generates an auditable 10-point data quality report.
3. Proprietary competition files placed in `data/raw/rr_competition/` are protected by `.gitignore` and are never exposed or committed.
4. If no external file is supplied, the platform automatically leverages authentic benchmark records of recent domestic performers cross-checked against Cricsheet ball-by-ball deliveries. Synthetic test fixtures are strictly isolated in `data/sample/` for QA only.

---

## 📄 Strategy Report & Presentation Export Instructions

To generate the competition deliverables:
- **Interactive Download:** Navigate to **Page 17 (Scouting Reports)** in the Streamlit web app to download the formatted PDF dossier and 16-slide PowerPoint deck with one click.
- **Programmatic Generation via Python CLI:**
```bash
# Generate PDF Strategy Report
python -c "from reports.executive_summary import ExecutiveSummaryPDFGenerator; ExecutiveSummaryPDFGenerator.generate_pdf('reports/RR_TalentIQ_Strategy_Report.pdf'); print('PDF created successfully!')"

# Generate 16-Slide PPTX Strategy Deck
python -c "from reports.presentation_export import PresentationDeckGenerator; PresentationDeckGenerator.generate_presentation_deck('reports/RR_TalentIQ_Strategy_Deck.pptx'); print('PPTX created successfully!')"
```


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
