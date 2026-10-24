"""
IPL Analytics Pro - Plotly Chart Components
Provides high-performance interactive Plotly charts adhering to the dark sports analytics design system.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

CHART_THEME = {
    "paper_bgcolor": "rgba(28, 37, 65, 0.4)",
    "plot_bgcolor": "rgba(11, 19, 43, 0.6)",
    "font": {"color": "#F8FAFC", "family": "Segoe UI, sans-serif"},
    "margin": dict(l=40, r=30, t=50, b=40),
}

COLOR_PALETTE = ["#FFB703", "#48CAE4", "#FB8500", "#0077B6", "#06D6A0", "#EF476F", "#9B5DE5", "#F15BB5"]

def style_fig(fig, title: str = ""):
    """Applies global dark theme styling, grid styling, and margins to a Plotly figure."""
    fig.update_layout(
        title={"text": f"<b>{title}</b>", "font": {"size": 15, "color": "#FFFFFF"}, "x": 0.02},
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=CHART_THEME["font"],
        margin=CHART_THEME["margin"],
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11)
        )
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)", zeroline=False)
    return fig

# 1. Season-wise Matches Played
def plot_season_matches(trends_df: pd.DataFrame):
    fig = px.bar(
        trends_df,
        x="Season",
        y="Matches",
        text="Matches",
        color_discrete_sequence=["#48CAE4"]
    )
    fig.update_traces(textposition="outside", marker_line_color="#0077B6", marker_line_width=1)
    return style_fig(fig, "Matches Played per Season (2008–2026)")

# 2. Season-wise Total Runs & Average Runs per Match
def plot_scoring_trends(trends_df: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=trends_df["Season"],
        y=trends_df["Total Runs"],
        name="Total Runs",
        marker_color="rgba(255, 183, 3, 0.8)",
        yaxis="y1"
    ))
    fig.add_trace(go.Scatter(
        x=trends_df["Season"],
        y=trends_df["Avg Runs/Match"],
        name="Avg Runs / Match",
        mode="lines+markers",
        line=dict(color="#48CAE4", width=3),
        marker=dict(size=8, symbol="circle"),
        yaxis="y2"
    ))
    fig.update_layout(
        yaxis=dict(title="Total Tournament Runs", side="left", showgrid=False),
        yaxis2=dict(title="Avg Runs per Match", side="right", overlaying="y", showgrid=False)
    )
    return style_fig(fig, "Tournament Run Volume & Match Scoring Rate")

# 3. Team Wins (All-Time Leaderboard)
def plot_team_wins(team_summary_df: pd.DataFrame):
    df_sorted = team_summary_df.sort_values("Won", ascending=True).tail(12)
    fig = px.bar(
        df_sorted,
        x="Won",
        y="Team",
        orientation="h",
        text="Won",
        color="Win %",
        color_continuous_scale="Viridis"
    )
    fig.update_traces(textposition="outside")
    return style_fig(fig, "Most Successful Franchises by Match Wins")

# 4. Batting First vs Chasing Comparison
def plot_bat_first_vs_chasing(matches_df: pd.DataFrame):
    valid = matches_df[matches_df["result_type"].isin(["runs", "wickets"])]
    counts = valid["result_type"].map({"runs": "Batting 1st (Defending)", "wickets": "Chasing (Batting 2nd)"}).value_counts().reset_index()
    counts.columns = ["Outcome", "Count"]
    fig = px.pie(
        counts,
        values="Count",
        names="Outcome",
        hole=0.45,
        color_discrete_sequence=["#FFB703", "#0077B6"]
    )
    fig.update_traces(textinfo="percent+label+value", marker=dict(line=dict(color="#0B132B", width=2)))
    return style_fig(fig, "Match Equity: Defending vs Chasing Outcomes")

# 5. Toss Impact: Toss Winner vs Match Winner
def plot_toss_vs_match_win(matches_df: pd.DataFrame):
    valid = matches_df[matches_df["winner"] != "No Result"].copy()
    valid["Toss_Won_Match_Won"] = valid["toss_winner"] == valid["winner"]
    toss_counts = valid["Toss_Won_Match_Won"].map({True: "Won Toss & Match", False: "Won Toss & Lost Match"}).value_counts().reset_index()
    toss_counts.columns = ["Result", "Matches"]
    fig = px.bar(
        toss_counts,
        x="Result",
        y="Matches",
        text="Matches",
        color="Result",
        color_discrete_sequence=["#06D6A0", "#EF476F"]
    )
    fig.update_traces(textposition="outside")
    return style_fig(fig, "Toss Win Conversion Equity")

# 6. Toss Decisions by Season (Stacked Bar)
def plot_toss_decisions_by_season(matches_df: pd.DataFrame):
    toss_df = matches_df.groupby(["season", "toss_decision"])["match_id"].count().reset_index()
    toss_df["toss_decision"] = toss_df["toss_decision"].map({"bat": "Chose to Bat", "field": "Chose to Field"})
    fig = px.bar(
        toss_df,
        x="season",
        y="match_id",
        color="toss_decision",
        barmode="stack",
        color_discrete_map={"Chose to Bat": "#FFB703", "Chose to Field": "#48CAE4"},
        labels={"match_id": "Matches", "season": "Season", "toss_decision": "Decision"}
    )
    return style_fig(fig, "Evolution of Toss Tactics Across Seasons")

# 7. Top 10 Run Scorers
def plot_top_run_scorers(batters_df: pd.DataFrame):
    df_sorted = batters_df.sort_values("Runs", ascending=True)
    fig = px.bar(
        df_sorted,
        x="Runs",
        y="striker",
        orientation="h",
        text="Runs",
        color="Strike_Rate",
        color_continuous_scale="Plasma",
        labels={"striker": "Batter", "Runs": "Total Runs", "Strike_Rate": "Strike Rate"}
    )
    fig.update_traces(textposition="outside")
    return style_fig(fig, "Top Run Scorers in IPL History")

# 8. Top 10 Wicket Takers
def plot_top_wicket_takers(bowlers_df: pd.DataFrame):
    df_sorted = bowlers_df.sort_values("Wickets", ascending=True)
    fig = px.bar(
        df_sorted,
        x="Wickets",
        y="bowler",
        orientation="h",
        text="Wickets",
        color="Economy",
        color_continuous_scale="Teal",
        labels={"bowler": "Bowler", "Wickets": "Wickets", "Economy": "Economy"}
    )
    fig.update_traces(textposition="outside")
    return style_fig(fig, "Leading Wicket Takers (Bowler-Credited)")

# 9. Batter Strike Rate vs Average Scatter Plot
def plot_batting_scatter(batters_df: pd.DataFrame):
    qual = batters_df[batters_df["Runs"] >= 1000].copy()
    fig = px.scatter(
        qual,
        x="Average",
        y="Strike_Rate",
        size="Runs",
        color="Sixes",
        hover_name="striker",
        color_continuous_scale="Viridis",
        labels={"Average": "Batting Average", "Strike_Rate": "Strike Rate", "Sixes": "6s"}
    )
    return style_fig(fig, "Efficiency Frontier: Batting Average vs Strike Rate (Min 1,000 Runs)")

# 10. Boundaries Trend (Fours and Sixes)
def plot_boundaries_trend(trends_df: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=trends_df["Season"],
        y=trends_df["Fours"],
        name="Fours (4s)",
        mode="lines+markers",
        line=dict(color="#48CAE4", width=2.5),
        marker=dict(size=7)
    ))
    fig.add_trace(go.Scatter(
        x=trends_df["Season"],
        y=trends_df["Sixes"],
        name="Sixes (6s)",
        mode="lines+markers",
        line=dict(color="#FFB703", width=2.5),
        marker=dict(size=7, symbol="diamond")
    ))
    return style_fig(fig, "Boundary Hitting Evolution Across Seasons")

# 11. Venue Matches Distribution
def plot_venue_matches(venues_df: pd.DataFrame):
    top_venues = venues_df.sort_values("Matches", ascending=True).tail(12)
    fig = px.bar(
        top_venues,
        x="Matches",
        y="Venue",
        orientation="h",
        text="Matches",
        color="Avg 1st Inn Score",
        color_continuous_scale="Turbo",
        labels={"Venue": "Stadium", "Matches": "Matches Hosted"}
    )
    fig.update_traces(textposition="outside")
    return style_fig(fig, "Top IPL Stadiums by Matches Hosted")

# 12. Head-to-Head Comparison Chart
def plot_head_to_head_summary(h2h_data: dict):
    team1 = h2h_data["team1"]
    team2 = h2h_data["team2"]
    labels = [team1, team2]
    wins = [h2h_data["team1_wins"], h2h_data["team2_wins"]]
    
    fig = go.Figure(data=[
        go.Bar(name="Wins", x=labels, y=wins, text=wins, textposition="auto", marker_color=["#FFB703", "#0077B6"])
    ])
    return style_fig(fig, f"Head-to-Head Win Tally: {team1} vs {team2}")

# 13. Team Score Distribution Box Plot
def plot_team_score_distribution(matches_df: pd.DataFrame):
    scores_list = []
    for _, row in matches_df.iterrows():
        if row["team1_score"] > 0:
            scores_list.append({"Team": row["team1"], "Score": row["team1_score"], "Innings": "1st Innings"})
        if row["team2_score"] > 0:
            scores_list.append({"Team": row["team2"], "Score": row["team2_score"], "Innings": "2nd Innings"})
            
    df_scores = pd.DataFrame(scores_list)
    top_teams = matches_df["team1"].value_counts().head(8).index
    df_filtered = df_scores[df_scores["Team"].isin(top_teams)]
    
    fig = px.box(
        df_filtered,
        x="Team",
        y="Score",
        color="Team",
        points="outliers",
        color_discrete_sequence=COLOR_PALETTE
    )
    return style_fig(fig, "Innings Score Distribution Across Major Franchises")
