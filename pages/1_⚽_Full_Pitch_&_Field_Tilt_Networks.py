import plotly.offline as pyo
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import json
from io import BytesIO
import numpy as np
from mplsoccer.pitch import Pitch, VerticalPitch
from mplsoccer import PyPizza, Radar
from highlight_text import fig_text
import matplotlib.pyplot as plt
import utils
import plotly.express as px


# Page config
st.set_page_config(
    page_icon="⚽️",
    layout="wide"
)


@st.cache_data
def load_data():
    # Load the df
    df = pd.read_csv("data/df_final - Copia.csv", sep=";")
    cosine = pd.read_csv("data/df_cosine_2.csv", sep=";")
    return df, cosine


df, cosine = load_data()

max_value = max(df.val_num)


with st.sidebar:
    st.image(
        "logo.png",
        use_column_width=True)
    with st.form('Form1'):
        player = st.selectbox("Select a Player", df.full_name)
        age = st.slider('Select a range for Age',
                        min(df.Age), max(df.Age), (min(df.Age), max(df.Age)))
        foot = st.selectbox('Preferred foot', ['All', 'Right', 'Left'])
        Number = st.slider("Number of result", 0, 10)
        value = st.slider('Market Value',
                          0, int(max_value/1000), (0, int(max_value/1000)), step=50)
        compare = st.selectbox('Comparison with', [
            'All positions', 'Defenders', 'Midfielders', 'Strikers'])

        run_1 = st.form_submit_button('Run')

if 'count' not in st.session_state:
    st.session_state.count = 0
if 'count2' not in st.session_state:
    st.session_state.count2 = 0

if not run_1 and st.session_state.count == 0:
    st.markdown(
        """
        <style>
        u {
            text-decoration: underline;
            text-decoration-color: #fa4d00;
            }
        </style>
        ### Welcome to the WNBA Player Analysis App!\n
        ##### This app runs an in-depth analysis on <u>any of the 990 players</u> \
        to ever attempt a field goal <u>in WNBA history (1997-2021)</u>. It leverages results from \
        an extremely calibrated, tuned, and accurate <u>machine learning model</u> that uses 16 features \
        to calculate <u>predicted probabilities</u> for the result of any given shot and turns it into an \
        interactive UI. Insights include over/underperforming players, player strengths and weaknesses, and more. \n
        ##### To start, use the sidebar on the left to choose a player and range of years.
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([.00001, 16, .00001])

    with col1:
        st.write(' ')

    with col2:
        st.image('foot.png', width=900)

    with col3:
        st.write(' ')
    st.session_state.count += 1


elif st.session_state.count2 > 0 or run_1:
    st.session_state.count2 += 1
    st.title("Scouting app")
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

    df_filt_2 = df_filt.sort_values(by=['sim_to'], ascending=False)[['name', 'cluster_bay', 'cluster_0', 'cluster_1',                                                     'cluster_2', 'cluster_3', 'cluster_4', 'cluster_5', 'cluster_6', 'cluster_7', 'cluster_8', 'cluster_9', 'cluster_10', 'cluster_11', 'hybrid',
                                                                    'sim_to']].head(Number)

    check_columns = ['cluster_0', 'cluster_1',                                                     'cluster_2',
                     'cluster_3', 'cluster_4', 'cluster_5', 'cluster_6', 'cluster_7', 'cluster_8', 'cluster_9', 'cluster_10', 'cluster_11', 'hybrid']

    to_add_columns = []
    for i in check_columns:
        if df_filt_2[i].sum() != 0:
            to_add_columns.append(i)

    sure = ['name', 'sim_to', 'cluster_bay']
    sure.extend(to_add_columns)

    # Display a static table
    st.dataframe(df_filt_2[sure])

    # Team selection
    st.subheader("Select players to compare")

    st.session_state['button2'] = True

    player_2 = st.selectbox(
        "Player",
        df_filt.sort_values(by=['sim_to'],
                            ascending=False).head(Number).name
    )

    metriche = ['% Cross riusciti',
                '% Cross vincenti',
                '% Cut Back riusciti',
                '% Cut Back vincenti',
                '% dribbling perdenti subiti',
                '% dribbling vincenti',
                '% duelli arei vinti',
                '% duelli tackle vinti',
                '% duelli vinti',
                '% duelli vinti nella metà campo offensiva',
                '% lanci +',
                '% lanci su gioco portiere',
                '% parate su tiri in porta subiti',
                '% passaggi +',
                '% Passaggi riusciti',
                '% passaggi su gioco portiere',
                '% Realizzazione',
                '% Traversoni riusciti',
                '% Traversoni vincenti',
                'Ammonizioni_p90',
                'Assist_p90',
                'Count High Acceleration OTIP_p90',
                'Count High Acceleration TIP_p90',
                'Count High Deceleration OTIP_p90',
                'Count High Deceleration TIP_p90',
                'Count HSR OTIP_p90',
                'Count HSR TIP_p90',
                'Count Medium Acceleration OTIP_p90',
                'Count Medium Acceleration TIP_p90',
                'Count Medium Deceleration OTIP_p90',
                'Count Medium Deceleration TIP_p90',
                'Count Sprint OTIP_p90',
                'Count Sprint TIP_p90',
                'Cross_p90',
                'Cut Back_p90',
                'Distance OTIP_p90',
                'Distance TIP_p90',
                'Dribbling_p90',
                'Duelli aerei_p100',
                'Duelli di gioco_p100',
                'Duelli nella metà campo offensiva_p100',
                'Duelli tackle_p100',
                'Espulsioni_p90',
                'Falli fatti_p100',
                'Falli subiti_p90',
                'HI Distance OTIP_p90',
                'HI Distance TIP_p90',
                'HSR Distance OTIP_p90',
                'HSR Distance TIP_p90',
                'In Fuorigioco_p90',
                'opxA',
                'opxG',
                'Palle Laterali_p90',
                'Passaggi Chiave ricevuti_p90',
                'Passaggi Chiave_p90',
                'Recupera palla_p100',
                'Third pass_p90',
                'Tiri da area_p90',
                'Tiri di testa_p90',
                'Tiri fuori area_p90',
                'Tiri_p90',
                'Traversoni_p90',
                'Triangolazioni_p90',
                ]

    params = st.multiselect(
        "Metric to compare",
        sorted(metriche),
        help="Select 10 metrics to compare with"
    )

    cluster_2 = df[df.full_name == player_2].cluster_bay.values[0]
    cluster_1 = df[df.full_name == player].cluster_bay.values[0]
    ruolo_2 = df[df.full_name == player_2].Ruolo.values[0]
    ruolo_1 = df[df.full_name == player].Ruolo.values[0]

    if cluster_2 == cluster_1:
        metriche_rank = []
        for m in metriche:
            m2 = m+'_rank'
            metriche_rank.append(m2)
            if m2 not in df[df.cluster_bay == cluster_2].columns:
                df[m2] = 100*df[m].rank(pct=True)
    elif ruolo_2 == ruolo_1:
        metriche_rank = []
        for m in metriche:
            m2 = m+'_rank'
            metriche_rank.append(m2)
            if m2 not in df[df.Ruolo == ruolo_2].columns:
                df[m2] = 100*df[m].rank(pct=True)
    else:
        metriche_rank = []
        for m in metriche:
            m2 = m+'_rank'
            metriche_rank.append(m2)
            if m2 not in df.columns:
                df[m2] = 100*df[m].rank(pct=True)

    params2 = []
    for i in params:
        p2 = i+'_rank'
        params2.append(p2)

    # for Vlahovic
    values = df[df.full_name == player][params2].values[0]
    values_2 = df[df.full_name == player_2][params2].values[0]

    params = [*params, params[0]]

    values = [*values, values[0]]
    values_2 = [*values_2, values_2[0]]

    fig = go.Figure(
        data=[
            go.Scatterpolar(r=values, theta=params,
                            fill='toself', fillcolor='lightcoral', name=f'{player}', line_color='red',
                            opacity=0.5,  mode='lines+text+markers', textposition='bottom center',
                            marker=dict(color='red')
                            ),
            go.Scatterpolar(r=values_2, theta=params, fillcolor='cornflowerblue', opacity=0.5,  mode='lines+text+markers', textposition='bottom center', line_color='blue',
                            marker=dict(color='blue'),
                            fill='toself', name=f'{player_2}'),
        ],
        layout=go.Layout(
            title=go.layout.Title(text='Player comparison'),
            polar={'radialaxis': {'visible': True}},
            showlegend=True
        )


    )

    # adjust layout
    fig.update_layout(
        template="plotly_dark",
        polar=dict(radialaxis=dict(gridwidth=0.5,
                                   showticklabels=True, ticks='', gridcolor="grey")))

    st.plotly_chart(fig)

    mkt = ['full_name',
           'birth_date',
           'country',
           'Current club',
           'Età',
           'Ruolo',
           'cluster_bay',
           'Height',
           'Citizenship',
           'Foot',
           'Joined',
           'Contract expires',
           'Outfitter',
           'Player agent',
           'Max_Val',
           'Date_Max_Val',
           'Valore',
           'Date of last contract extension',
           'Contract option',
           'On loan from',
           'Contract there expires',
           '2nd club',
           '3nd club'
           ]

    bio = ['full_name', 'Squad',
           'Starting eleven',
           'Substituted in',
           'On the bench',
           'Suspended',
           'Injured']

    col1, col2 = st.columns([0.7, 0.8])

    with col1:
        st.dataframe(df[(df.full_name == player) |
                        (df.full_name == player_2)][mkt].transpose())

    st.write('')

    with col2:
        st.dataframe(df[(df.full_name == player) |
                        (df.full_name == player_2)][bio].transpose())


else:
    st.write('ppapsp')
