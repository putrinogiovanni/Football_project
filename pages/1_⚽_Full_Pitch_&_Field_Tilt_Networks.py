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
    # Load the df
    df = pd.read_csv("data/df_final - Copia.csv", sep=";")
    cosine = pd.read_csv("data/df_cosine_2.csv", sep=";")
    return df, cosine


df, cosine = load_data()

# Page title
st.title("Scouting app")

col1, col2, col3 = st.columns([1, 1, 0.8])
with col1:
    player = st.selectbox("Player", df.full_name)
with col2:
    age = st.slider('Select a range for Age',
                    min(df.Age), max(df.Age), (min(df.Age), max(df.Age)))
with col3:
    foot = st.selectbox('Preferred foot', ['All', 'Right', 'Left'])

st.write('')

max_value = max(df.val_num)

col4, col5, col6 = st.columns([1, 1, 0.8])
with col4:
    Number = st.slider("Number of result", 0, 10)
with col5:
    value = st.slider('Market Value',
                      0, int(max_value/1000), (0, int(max_value/1000)), step=50)
with col6:
    compare = st.selectbox('Comparison with', [
                           'All positions', 'Defenders', 'Midfielders', 'Strikers'])

st.write(
    f"Selected player belongs to cluster {df[df.full_name==player].cluster_bay.values[0]}")

df['sim_to'] = cosine[player]

if compare == 'Defenders':
    role = 'D'
elif compare == 'Midfielders':
    role = 'C'
elif compare == 'Strikers':
    role = 'A'
else:
    role = 'All'

if role == 'All' and foot != 'All':
    df_filt = df[(df.Age.between(age[0], age[1])) & (df.val_num.between(
        value[0]*1000, value[1]*1000)) & ((df.Foot == foot.lower) | (df.Foot == 'both'))]
elif role == 'All' and foot == 'All':
    df_filt = df[(df.Age.between(age[0], age[1])) & (
        df.val_num.between(value[0]*1000, value[1]*1000))]
elif role != 'All' and foot == 'All':
    df_filt = df[(df.Age.between(age[0], age[1])) & (
        df.val_num.between(value[0]*1000, value[1]*1000)) & (df.Ruolo == role)]
else:
    df_filt = df[(df.Age.between(age[0], age[1])) & (df.val_num.between(
        value[0]*1000, value[1]*1000)) & (df.Ruolo == role) & ((df.Foot == foot.lower) | (df.Foot == 'both'))]


st.dataframe(df_filt.sort_values(by=['sim_to'], ascending=False)[['name', 'cluster_bay', 'cluster_0', 'cluster_1',                                                     'cluster_2', 'cluster_3', 'cluster_4', 'cluster_5', 'cluster_6', 'cluster_7', 'cluster_8', 'cluster_9', 'cluster_10', 'cluster_11', 'hybrid',
                                                                  'sim_to']].head(Number))


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


params_rank = []
for m in parms2:
    m2 = m+'_rank'
    metriche_rank.append(m2)
    if m2 not in df.columns:
        df2[m2] = 100*df2[m].rank(pct=True)


if team_selection == "First Player":
    utils.pizza_chart(parms2, df[df.full_name == player][parms2].values, df.sort_values(
        by=['sim_to'], ascending=False).head(1).values)

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
