import streamlit as st
import pandas as pd
import json
from io import BytesIO

import utils

# Page config
st.set_page_config(
    page_icon="⚽️",
    layout="wide"
)

# Load data
@st.cache
def load_data():
    # Load the edited Soccerment allEvents dataset
    df_soccment = pd.read_csv("data/soccerment_serieA_2021-22_allEvents_EDIT.csv")
    # Load lineups.json, manually created from "Appendix 5 - Formations Explained"
    with open("data/lineups.json", "r") as f:
        lineups = json.load(f)
    # Load teams_lineups.json 
    with open("data/teams_lineups.json", "r") as f:
        teams_lineups = json.load(f)
    # Load teams_match_status.json
    with open("data/teams_match_status.json", "r") as f:
        teams_match_status = json.load(f)
    return df_soccment, lineups, teams_lineups, teams_match_status

df_soccment, lineups, teams_lineups, teams_match_status = load_data()


# Page title
st.title("Match Status Networks")

# Matchdays selection
st.subheader("Select matchday(s)")

matchday_selection_2 = st.radio(
    "Matchday visualization",
    ("Single matchday", "Range of matchdays")
)
if matchday_selection_2 == "Single matchday":
    matchday = st.selectbox(
        "Matchday",
        (range(1,39))
    )
    matchday_list = [matchday]
else:
    matchday_tuple = st.slider("Range of matchdays", 1, 38, (1, 38))
    min_match, max_match = matchday_tuple
    matchday_list = range(min_match, max_match+1)

# Team selection
st.subheader("Select team")

team = st.selectbox(
    "Team",
    (sorted(teams_lineups.keys()))
)

# Additional parameters for the visualization
st.subheader("Select the number of minimum passes to visualize")

# Insert number of minimum passes for the visualization
filter_passes_unit = st.number_input("Number of minimum passes", min_value=1, max_value=20, value=5, help="For multiple matchdays, this value is NOT multiplied by the number of matchdays.")

# Keep GK in barycenter computation
st.subheader("Select whether or not to keep the goalkeeper in barycenter computation")

exclude_gk = st.checkbox("Exclude GK")

# Put a little vertical space
st.text("")

# Run analysis
run_analysis = st.button("Run analysis", type="primary")
if run_analysis:
    # Plot team info
    fig_bars = utils.plot_team_match_status_formation_info(team, matchday_list, teams_match_status, teams_lineups)
    buf = BytesIO()
    fig_bars.savefig(buf, format="png")
    st.image(buf, use_column_width="auto")

    # Plot passing networks
    fig_pitch = utils.plot_match_status_networks(df_soccment, team, matchday_list, teams_lineups, filter_passes_unit, exclude_gk)
    buf = BytesIO()
    fig_pitch.savefig(buf, format="png")
    st.image(buf, use_column_width="auto")
