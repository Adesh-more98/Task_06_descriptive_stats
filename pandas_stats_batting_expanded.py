#!/usr/bin/env python3
"""
pandas_stats_batting_expanded.py

Expanded descriptive statistics for a cricket batting scorecard (Task 05).
Adds more metrics and optional CSV outputs.

Usage:
    python pandas_stats_batting_expanded.py --csv /path/to/batting_card.csv --outdir outputs --min-balls 10
"""
import argparse
import os
from pathlib import Path
import pandas as pd

NUMERIC_COLS = [
    "runs",
    "ballsFaced",
    "fours",
    "sixes",
    "strikeRate",
]

def coerce_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def add_helper_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived metrics used across summaries."""
    if {"fours", "sixes"}.issubset(df.columns):
        df["boundaries"] = df["fours"].fillna(0) + df["sixes"].fillna(0)
        df["boundary_runs"] = df["fours"].fillna(0) * 4 + df["sixes"].fillna(0) * 6
    if {"runs", "ballsFaced"}.issubset(df.columns):
        # Runs per ball is a stable metric even if SR missing
        df["runs_per_ball"] = df.apply(
            lambda r: (r["runs"] / r["ballsFaced"]) if pd.notnull(r["runs"]) and pd.notnull(r["ballsFaced"]) and r["ballsFaced"] > 0 else pd.NA,
            axis=1
        )
        # Boundary % of runs
        df["boundary_pct_of_runs"] = df.apply(
            lambda r: (r["boundary_runs"] / r["runs"] * 100.0) if pd.notnull(r.get("boundary_runs", pd.NA)) and pd.notnull(r["runs"]) and r["runs"] > 0 else pd.NA,
            axis=1
        )
    return df

def compute_core_stats(df: pd.DataFrame, min_balls: int = 10) -> dict:
    res = {}
    res["average_runs"] = float(df["runs"].mean())
    res["total_runs"] = int(df["runs"].fillna(0).sum())
    res["total_boundaries"] = int(df.get("boundaries", pd.Series([0]*len(df))).fillna(0).sum())
    res["total_boundary_runs"] = int(df.get("boundary_runs", pd.Series([0]*len(df))).fillna(0).sum())

    res["top5_run_scorers"] = (
        df[["name", "runs"]]
        .sort_values("runs", ascending=False)
        .head(5)
        .reset_index(drop=True)
    )

    qualified = df[df["ballsFaced"] >= min_balls].copy()
    if not qualified.empty and "strikeRate" in df.columns:
        res["top_strike_rate"] = (
            qualified[["name", "strikeRate", "runs", "ballsFaced"]]
            .sort_values("strikeRate", ascending=False)
            .head(5)  # top 5 for better visualization
            .reset_index(drop=True)
        )
    else:
        res["top_strike_rate"] = pd.DataFrame(columns=["name", "strikeRate", "runs", "ballsFaced"])

    res["most_sixes"] = (
        df[["name", "sixes"]]
        .sort_values("sixes", ascending=False)
        .head(5)
        .reset_index(drop=True)
    )

    res["most_fours"] = (
        df[["name", "fours"]]
        .sort_values("fours", ascending=False)
        .head(5)
        .reset_index(drop=True)
    )

    if "ballsFaced" in df.columns:
        res["most_balls_faced"] = (
            df[["name", "ballsFaced"]]
            .sort_values("ballsFaced", ascending=False)
            .head(5)
            .reset_index(drop=True)
        )

    # Efficiency metrics
    if "runs_per_ball" in df.columns:
        eff = df.dropna(subset=["runs_per_ball"])[["name", "runs", "ballsFaced", "runs_per_ball"]]
        res["best_runs_per_ball"] = eff.sort_values("runs_per_ball", ascending=False).head(5).reset_index(drop=True)
    else:
        res["best_runs_per_ball"] = pd.DataFrame(columns=["name", "runs", "ballsFaced", "runs_per_ball"])

    if "boundary_pct_of_runs" in df.columns:
        bpr = df.dropna(subset=["boundary_pct_of_runs"])[["name", "runs", "boundary_runs", "boundary_pct_of_runs"]]
        res["best_boundary_ratio"] = bpr.sort_values("boundary_pct_of_runs", ascending=False).head(5).reset_index(drop=True)
    else:
        res["best_boundary_ratio"] = pd.DataFrame(columns=["name", "runs", "boundary_runs", "boundary_pct_of_runs"])

    return res

def aggregates(df: pd.DataFrame) -> dict:
    out = {}
    # Per-player across rows (if players appear multiple times)
    if "name" in df.columns:
        out["per_player_totals"] = (
            df.groupby("name")
            .agg(
                innings=("name", "count"),
                total_runs=("runs", "sum"),
                avg_runs=("runs", "mean"),
                max_score=("runs", "max"),
                total_fours=("fours", "sum"),
                total_sixes=("sixes", "sum"),
                avg_sr=("strikeRate", "mean"),
                total_balls=("ballsFaced", "sum"),
            )
            .sort_values("total_runs", ascending=False)
            .reset_index()
        )
    # Per-match if available
    if "match_id" in df.columns:
        out["per_match_totals"] = (
            df.groupby("match_id")
            .agg(
                total_runs=("runs", "sum"),
                max_individual=("runs", "max"),
                avg_sr=("strikeRate", "mean"),
                entries=("name", "count"),
            )
            .reset_index()
        )
    return out

def print_summary(res: dict):
    print("\n=== Expanded Batting Descriptive Statistics ===")
    print(f"• Average Runs per entry: {res['average_runs']:.2f}")
    print(f"• Total Runs: {res['total_runs']}")
    print(f"• Total Boundaries (4s + 6s): {res['total_boundaries']}")
    print(f"• Total Boundary Runs (4*4s + 6*6s): {res['total_boundary_runs']}")

    print("\n• Top 5 Run Scorers:")
    print(res["top5_run_scorers"].to_string(index=False))

    print("\n• Highest Strike Rates (min balls faced filter applied, Top 5):")
    if res["top_strike_rate"].empty:
        print("  No players qualified for the strike-rate leaderboard.")
    else:
        print(res["top_strike_rate"].to_string(index=False))

    print("\n• Most Sixes (Top 5):")
    print(res["most_sixes"].to_string(index=False))

    print("\n• Most Fours (Top 5):")
    print(res["most_fours"].to_string(index=False))

    if "most_balls_faced" in res:
        print("\n• Most Balls Faced (Top 5):")
        print(res["most_balls_faced"].to_string(index=False))

    print("\n• Best Runs per Ball (Top 5):")
    print(res["best_runs_per_ball"].to_string(index=False))

    print("\n• Highest Boundary % of Runs (Top 5):")
    print(res["best_boundary_ratio"].to_string(index=False))

def save_outputs(res: dict, aggs: dict, outdir: str | None):
    if not outdir:
        return
    Path(outdir).mkdir(parents=True, exist_ok=True)

    # Save result frames
    for key in ["top5_run_scorers", "top_strike_rate", "most_sixes", "most_fours", "most_balls_faced", "best_runs_per_ball", "best_boundary_ratio"]:
        if key in res and isinstance(res[key], pd.DataFrame):
            res[key].to_csv(os.path.join(outdir, f"{key}.csv"), index=False)

    # Save aggregates
    for k, v in aggs.items():
        v.to_csv(os.path.join(outdir, f"{k}.csv"), index=False)

    # Save scalars
    scalars = {
        "average_runs": res.get("average_runs"),
        "total_runs": res.get("total_runs"),
        "total_boundaries": res.get("total_boundaries"),
        "total_boundary_runs": res.get("total_boundary_runs"),
    }
    pd.DataFrame([scalars]).to_csv(os.path.join(outdir, "scalar_summary_expanded.csv"), index=False)

    print(f"\n✔ Expanded results written to: {Path(outdir).resolve()}")

def main():
    parser = argparse.ArgumentParser(description="Expanded descriptive stats for a cricket batting scorecard.")
    parser.add_argument("--csv", required=True, help="Path to batting_card.csv")
    parser.add_argument("--outdir", default=None, help="Directory to save CSV outputs (optional)")
    parser.add_argument("--min-balls", type=int, default=10, help="Minimum balls faced for strike-rate leaderboard")
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    df = coerce_numeric(df, NUMERIC_COLS)
    df = add_helper_columns(df)

    # Validate minimum required columns
    required = {"name", "runs"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Required columns missing: {missing}")

    res = compute_core_stats(df, min_balls=args.min_balls)
    aggs = aggregates(df)
    print_summary(res)
    save_outputs(res, aggs, args.outdir)

if __name__ == "__main__":
    main()
