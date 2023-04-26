import streamlit as st
import pandas as pd
import json
from io import BytesIO

from mplsoccer.pitch import Pitch, VerticalPitch
from mplsoccer import PyPizza, Radar
from highlight_text import fig_text

import utils

# Page config
st.set_page_config(
    page_icon="⚽️",
    layout="wide"
)


options = st.multiselect(
    'What are your favorite colors',
    ['Green', 'Yellow', 'Red', 'Blue'],
    ['Yellow', 'Red'])

st.write('You selected:', options[1])


# Load data


@st.cache_data
def load_data():
    # Load the edited Soccerment allEvents dataset
    df = pd.read_csv("data/df_final.csv")
    cosine = pd.read_csv("data/df_cosine.csv")
    return df, cosine


df, cosine = load_data()

# Page title
st.title("Scouting app")

# Matchdays selection
st.subheader("Select player")

player = st.selectbox(
    "Player", df.full_name
)


df['sim_to'] = cosine[player]
st.dataframe(df.sort_values(by=['sim_to'], ascending=False)[['name', 'cluster_bay', 'cluster_0', 'cluster_1',                                                     'cluster_2', 'cluster_3', 'cluster_4', 'cluster_5', 'cluster_6', 'cluster_7', 'cluster_8', 'cluster_9', 'cluster_10', 'cluster_11', 'hybrid',
                                                             'sim_to']].head(10))


# Team selection
st.subheader("Select players to compare")

team_selection = st.radio(
    "Player Selection",
    ("First Player", "First three players",
     "First five players", "First ten players")
)

parms2 = st.multiselect(
    "Team",
    (sorted(df.columns))
)


if team_selection == "First Player":
    pizza_chart(parms2, df[df.full_name == player][parms].values, df.sort_values(
        by=['sim_to'], ascending=False).head(1))

elif team_selection == "Two teams":
    team_list = st.multiselect(
        "First Player",
        sorted(teams_lineups.keys()),
        help="Select exactly two teams."
    )
    if len(team_list) > 2:
        st.warning("You have selected more than two teams!")
else:
    team_list = sorted(teams_lineups.keys())

# Additional parameters for the visualization
st.subheader("Select the area of the pitch for visualizing the passing network")

# Pitch zone for the passing network
pitch_zone_btn = st.radio(
    "Area of the pitch to visualize",
    ("Complete pitch (Full passing network)",
     "Final third (Field-tilt passing network)")
)
if pitch_zone_btn == "Complete pitch (Full passing network)":
    pitch_zone = "full"
else:
    pitch_zone = "field_tilt"


# Additional parameters for the visualization
st.subheader("Select the number of minimum passes")

# Insert number of minimum passes for the visualization
filter_passes_unit = st.number_input("Number of minimum passes", min_value=1, max_value=10,
                                     value=3, help="For multiple matchdays, this value is multiplied by the number of matchdays.")

# Put a little vertical space
st.text("")

# Run analysis
run_analysis = st.button("Run analysis", type="primary")
if run_analysis:
    if team_selection == "Single team":
        if matchday_selection_1 == "Single matchday":
            fig = utils.plot_single_matchday_single_team(
                df_soccment, team, matchday, teams_lineups, pitch_zone, filter_passes_unit)
        else:
            fig = utils.plot_multiple_matchdays_single_team(
                df_soccment, team, matchday_list, teams_lineups, pitch_zone, filter_passes_unit)
    elif team_selection == "Two teams":
        if matchday_selection_1 == "Single matchday":
            fig = utils.plot_single_matchday_two_teams(
                df_soccment, team_list, matchday, teams_lineups, pitch_zone, filter_passes_unit)
        else:
            fig = utils.plot_multiple_matchdays_two_teams(
                df_soccment, team_list, matchday_list, teams_lineups, pitch_zone, filter_passes_unit)
    else:
        if matchday_selection_1 == "Single matchday":
            fig = utils.plot_single_matchday_all_teams(
                df_soccment, team_list, matchday, teams_lineups, pitch_zone, filter_passes_unit)
        else:
            fig = utils.plot_multiple_matchdays_all_teams(
                df_soccment, team_list, matchday_list, teams_lineups, pitch_zone, filter_passes_unit)

    buf = BytesIO()
    fig.savefig(buf, format="png")
    st.image(buf, use_column_width="auto")
