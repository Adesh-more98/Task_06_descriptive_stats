#!/usr/bin/env python3
"""
visualize_batting.py

Simple Matplotlib visualizations for batting scorecard.
Generates bar charts for:
  - Top 5 run scorers
  - Most sixes (Top 5)
  - Highest strike rate (Top 5, min balls filter)

Usage:
    python visualize_batting.py --csv /path/to/batting_card.csv --outdir plots --min-balls 10
"""
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    for c in ["runs", "ballsFaced", "fours", "sixes", "strikeRate"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def top5_runs(df: pd.DataFrame) -> pd.DataFrame:
    return df[["name", "runs"]].sort_values("runs", ascending=False).head(5)

def top5_sixes(df: pd.DataFrame) -> pd.DataFrame:
    return df[["name", "sixes"]].sort_values("sixes", ascending=False).head(5)

def top5_strike_rate(df: pd.DataFrame, min_balls: int) -> pd.DataFrame:
    qualified = df[df["ballsFaced"] >= min_balls]
    if "strikeRate" not in df.columns or qualified.empty:
        return pd.DataFrame(columns=["name", "strikeRate"])
    return qualified[["name", "strikeRate"]].sort_values("strikeRate", ascending=False).head(5)

def save_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str, outpath: Path):
    plt.figure()
    plt.bar(df[x_col].astype(str), df[y_col])  # no custom colors/styles
    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()

def main():
    parser = argparse.ArgumentParser(description="Create bar charts for batting stats.")
    parser.add_argument("--csv", required=True, help="Path to batting_card.csv")
    parser.add_argument("--outdir", default="plots", help="Directory to save images")
    parser.add_argument("--min-balls", type=int, default=10, help="Minimum balls faced for strike-rate leaderboard")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.csv)
    df = coerce_numeric(df)

    runs_df = top5_runs(df)
    sixes_df = top5_sixes(df)
    sr_df = top5_strike_rate(df, args.min_balls)

    save_bar_chart(runs_df, "name", "runs", "Top 5 Run Scorers", outdir / "top5_runs.png")
    save_bar_chart(sixes_df, "name", "sixes", "Most Sixes (Top 5)", outdir / "top5_sixes.png")
    if not sr_df.empty:
        save_bar_chart(sr_df, "name", "strikeRate", "Highest Strike Rates (Top 5)", outdir / "top5_strike_rate.png")

    print(f"✔ Plots saved to {outdir.resolve()}")

if __name__ == "__main__":
    main()
