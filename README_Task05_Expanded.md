
# 🏏 Task 5 — Cricket Batting Data Analysis (Expanded Version)

## 📌 Overview
This project performs **descriptive statistics** and generates **visualizations** for a cricket batting scorecard using **Python + Pandas**.  
It builds on the original Task 5 submission, adding **more in-depth metrics**, **derived statistics**, and **visual charts**.

---

## 📂 Files in This Version

| File | Description |
|------|-------------|
| `pandas_stats_batting_expanded.py` | Main script — reads the batting CSV, calculates expanded statistics, and optionally saves them to CSV files. |
| `visualize_batting.py` | Generates Matplotlib bar charts for top performers (Top Runs, Sixes, Strike Rates). |
| `batting_card.csv` | Input dataset (sample cricket batting scorecard). |

---

## 🔍 What’s New in the Expanded Version
Compared to the original submission:
- **Additional Stats**:
  - Total runs, total boundaries, total boundary runs
  - Top 5 by **runs, strike rate, sixes, fours**
  - Most balls faced
  - Best runs-per-ball ratio
  - Highest % of runs from boundaries
- **Aggregates**:
  - Per-player totals across innings
  - Per-match summaries (if match_id exists)
- **Derived Columns**:
  - Boundaries = 4s + 6s
  - Boundary runs = (4×fours) + (6×sixes)
  - Runs per ball
  - Boundary % of runs
- **Export**:
  - Saves CSVs for all leaderboards and summary stats if `--outdir` is specified
- **Visualization**:
  - Bar charts for Top 5 run scorers, Most Sixes, and Highest Strike Rates

---

## ⚙️ How to Run

**1️⃣ Expanded Stats**
```bash
python pandas_stats_batting_expanded.py --csv batting_card.csv --outdir outputs --min-balls 10
```
- `--csv` → path to batting CSV
- `--outdir` → (optional) folder to save CSV outputs
- `--min-balls` → min balls faced for strike-rate leaderboard

**2️⃣ Visualizations**
```bash
python visualize_batting.py --csv batting_card.csv --outdir plots --min-balls 10
```
- Saves PNG bar charts to the specified folder

---

## 📊 Example Outputs

**Console Example:**
```
=== Expanded Batting Descriptive Statistics ===
• Average Runs per entry: 24.35
• Total Runs: 438
• Total Boundaries (4s + 6s): 56
• Total Boundary Runs (4*4s + 6*6s): 212

• Top 5 Run Scorers:
   name   runs
1  PlayerA   72
2  PlayerB   64
...
```

**Charts:**
- `top5_runs.png`
- `top5_sixes.png`
- `top5_strike_rate.png`

---

## 📚 Skills & Tools Used
- **Python**
- **Pandas**
- **Matplotlib**
- Data cleaning, aggregation, and feature engineering
- Cricket statistics interpretation
- Script parameterization (argparse)
