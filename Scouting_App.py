import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import json
import math
import numpy as np
from mplsoccer.pitch import Pitch, VerticalPitch
from mplsoccer import PyPizza, Radar
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import os


# Page config
st.set_page_config(
    layout="wide"
)

# load data


@st.cache_data
def load_data():
    # Load the df
    df = pd.read_csv("data/df_final.csv", sep=";")
    cosine = pd.read_csv("data/df_cosine.csv", sep=";")
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

        scad = st.checkbox('Expiring contract')

        run_1 = st.form_submit_button('Run')

# setto dei count per session state in modo che non mi si ristarti l'app tutte le volte che seleziono qualcosa dopo aver runnato
if 'count' not in st.session_state:
    st.session_state.count = 0
if 'count2' not in st.session_state:
    st.session_state.count2 = 0

if not run_1 and st.session_state.count == 0:
    # se ancora non ha mai runnato scrivi questo
    st.markdown(
        """
        <style>
        u {
            text-decoration: underline;
            text-decoration-color: #fa4d00;
            }
        </style>
        ### Welcome to the Player Scouting App!</u> \n
        ##### With this application you have the ability to scout the most similar players compared to the player given in input.\
        Similarity is calculated using cosine distance.\
        The search can be refined by choosing various metrics to filter on, such as age, market value, and preferred foot.\
        One can also choose from which categories of players to search and whether to search only for players with expiring contracts. \n
        ##### There is Cluster_Analysis page where the clusters and the methodology used are described, both for defining the similarity metric and for constructing the clusters \n
        ##### To start, use the sidebar on the left to choose number of result  that will be shown and click on "RUN" button.
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

    df['sim_to'] = cosine[player]

    if compare == 'Defenders':
        role = 'D'
    elif compare == 'Midfielders':
        role = 'C'
    elif compare == 'Strikers':
        role = 'A'
    else:
        role = 'All'

    if scad:
        df_copy = df.copy()
        df['scad_y'] = df['Contract expires'].apply(lambda x: int(relativedelta(datetime.strptime(datetime.strptime(x, '%b %d, %Y').strftime(
            '%Y-%m-%d'), '%Y-%m-%d'), datetime.strptime(datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')).years) if x != '-' else x)

        df = df[df.scad_y != '-']
        df = df[df.scad_y < 1]

    if role == 'All' and foot != 'All':
        df_filt = df[(df.Age.between(age[0], age[1])) & (df.val_num.between(
            value[0]*1000, value[1]*1000)) & ((df.Foot == foot.lower()) | (df.Foot == 'both'))]
    elif role == 'All' and foot == 'All':
        df_filt = df[(df.Age.between(age[0], age[1])) & (
            df.val_num.between(value[0]*1000, value[1]*1000))]
    elif role != 'All' and foot == 'All':
        df_filt = df[(df.Age.between(age[0], age[1])) & (
            df.val_num.between(value[0]*1000, value[1]*1000)) & (df.Ruolo == role)]
    else:
        df_filt = df[(df.Age.between(age[0], age[1])) & (df.val_num.between(
            value[0]*1000, value[1]*1000)) & (df.Ruolo == role) & ((df.Foot == foot.lower()) | (df.Foot == 'both'))]

    df_filt_2 = df_filt.sort_values(by=['sim_to'], ascending=False)[['name', 'cluster_bay', 'cluster_0', 'cluster_1',                                                     'cluster_2', 'cluster_3', 'cluster_4', 'cluster_5', 'cluster_6', 'cluster_7', 'cluster_8', 'cluster_9', 'cluster_10', 'cluster_11', 'hybrid',
                                                                    'sim_to']].head(Number)

    sure = ['name', 'sim_to', 'cluster_bay', 'cluster_0', 'cluster_1',                                                     'cluster_2',
            'cluster_3', 'cluster_4', 'cluster_5', 'cluster_6', 'cluster_7', 'cluster_8', 'cluster_9', 'cluster_10', 'cluster_11', 'hybrid']

    # Display a static table
    if Number == 0:
        st.write('Please select number of result to show and click "Run" to start')
    else:

        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown(
                f"Selected Player: **:red[{player}]**")
            if scad:
                st.markdown(
                    f"Role: **{df_copy[df_copy.full_name==player]['Ruolo'].values[0]}**")
                st.markdown(
                    f"Cluster: **{df_copy[df_copy.full_name==player]['cluster_bay'].values[0]}**")
                st.image(
                    f"seriea_loghi\\{df_copy[df_copy.full_name==player]['Current club'].values[0]}.png")
                st.text(
                    f"Joined on : {df_copy[df_copy.full_name==player]['Joined'].values[0]}")
                if not df_copy[df_copy.full_name == player]['On loan from'].isnull().iloc[0]:
                    st.text(
                        f"On loan from: {df_copy[df_copy.full_name==player]['On loan from'].values[0]}")
                    st.image(
                        f"seriea_loghi\\{df_copy[df_copy.full_name==player]['On loan from'].values[0]}.png")
            else:
                st.markdown(
                    f"Role: **{df[df.full_name==player]['Ruolo'].values[0]}**")
                st.markdown(
                    f"Cluster: **{df[df.full_name==player]['cluster_bay'].values[0]}**")
                st.image(
                    f"seriea_loghi\\{df[df.full_name==player]['Current club'].values[0]}.png")
                st.text(
                    f"Joined on : {df[df.full_name==player]['Joined'].values[0]}")
                if not df[df.full_name == player]['On loan from'].isnull().iloc[0]:
                    st.text(
                        f"On loan from: {df[df.full_name==player]['On loan from'].values[0]}")
                    st.image(
                        f"seriea_loghi\\{df[df.full_name==player]['On loan from'].values[0]}.png")

        with col2:
            st.write('Similarity Dataframe')
            st.write('')
            st.dataframe(df_filt_2[sure].dropna(axis=1, how='all'))

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
            help="Select metrics to compare with"
        )

        if len(params) == 0:
            st.write('')

        else:
            if scad:
                df = df_copy
            cluster_2 = df[df.full_name == player_2].cluster_bay.values[0]
            cluster_1 = df[df.full_name == player].cluster_bay.values[0]
            ruolo_2 = df[df.full_name == player_2].Ruolo.values[0]
            ruolo_1 = df[df.full_name == player].Ruolo.values[0]

            params2 = []
            for i in params:
                p2 = i+'_rank'
                params2.append(p2)

            if cluster_2 == cluster_1:
                df_sel = df[df.cluster_bay == cluster_1]
                sel_1 = 1
                metriche_rank = []
                for m in metriche:
                    m2 = m+'_rank'
                    metriche_rank.append(m2)
                    df_sel[m2] = 100 * df_sel[m].rank(pct=True)
                values = df_sel[df_sel.full_name == player][params2].values[0]
                values_2 = df_sel[df_sel.full_name ==
                                  player_2][params2].values[0]
            elif ruolo_2 == ruolo_1:
                df_sel = df[df.Ruolo == ruolo_1]
                sel_2 = 1
                metriche_rank = []
                for m in metriche:
                    m2 = m+'_rank'
                    metriche_rank.append(m2)
                    df_sel[m2] = 100 * df_sel[m].rank(pct=True)
                values = df_sel[df_sel.full_name == player][params2].values[0]
                values_2 = df_sel[df_sel.full_name ==
                                  player_2][params2].values[0]
            else:
                sel_3 = 1
                df_sel = df
                metriche_rank = []
                for m in metriche:
                    m2 = m+'_rank'
                    metriche_rank.append(m2)
                    df_sel[m2] = 100*df_sel[m].rank(pct=True)
                values = df_sel[df_sel.full_name == player][params2].values[0]
                values_2 = df_sel[df_sel.full_name ==
                                  player_2][params2].values[0]

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

            col1, col2, col3 = st.columns([1.5, 6, 1])

            with col1:
                st.write(' ')

            with col2:
                st.plotly_chart(fig)

            with col3:
                st.write(' ')

            mkt = ['full_name',
                   'birth_date',
                   'Età',
                   'Ruolo',
                   'cluster_bay',
                   'Foot',
                   'Height',
                   'Citizenship',
                   'country',
                   'Current club',
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
                   '3nd club',
                   'val_num'
                   ]

            sub_mkt = ['full_name',
                       'birth_date',
                       'Età',
                       'Ruolo',
                       'cluster_bay',
                       'Foot',
                       'Height',
                       'Citizenship',
                       'country',
                       'Current club',
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
                       '3nd club',
                       ]

            bio = ['full_name', 'Squad',
                   'Starting eleven',
                   'Substituted in',
                   'On the bench',
                   'Suspended',
                   'Injured']

            col1, col2 = st.columns([3, 2])

            with col1:

                df_t = df[(df.full_name == player) |
                          (df.full_name == player_2)]

                df_t['order'] = df_t.full_name.apply(
                    lambda x: 0 if x == player else 1)

                df_t.sort_values(by=['order'], ascending=True, inplace=True)

                df_t_t = df_t[mkt].set_index(
                    'full_name').transpose()

                df_t_sub = df_t[sub_mkt].set_index('full_name').transpose()

                st.text('💰📄 Bio and Market Comparison:')
                st.dataframe(df_t_sub.dropna(axis=0, how='all'))

            with col2:
                st.text('🔥🌡️ Status Comparison:')
                df_t_2 = df[(df.full_name == player) |
                            (df.full_name == player_2)][bio].set_index('full_name').transpose()
                st.dataframe(df_t_2.dropna(axis=0, how='all'))

            col1, col2, col3 = st.columns([1, 1, 1])

            st.write(
                """
            <style>
            [data-testid="stMetricDelta"] svg {
                display: none;
            }
            </style>
            """,
                unsafe_allow_html=True,
            )
            with col1:
                if df_t_t.loc['val_num'][1] - df_t_t.loc['val_num'][0] >= 0:
                    st.metric(label=f"{player_2} value:",
                              value="{:,}".format(df_t_t.loc['val_num'][1]), delta='+ '+"{:,}".format(df_t_t.loc['val_num'][1] - df_t_t.loc['val_num'][0]))
                else:
                    st.metric(label=f"Valore {player_2}",
                              value="{:,}".format(df_t_t.loc['val_num'][1]), delta="{:,}".format(df_t_t.loc['val_num'][1] - df_t_t.loc['val_num'][0]))

            with col2:
                if df_t_t.loc['Contract expires'][1] != '-':
                    rdelta = relativedelta(datetime.strptime(datetime.strptime(df_t_t.loc['Contract expires'][1], '%b %d, %Y').strftime(
                        '%Y-%m-%d'), '%Y-%m-%d'), datetime.strptime(datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d'))
                    st.metric(label=f"{player_2} contract expires",
                              value=df_t_t.loc['Contract expires'][1], delta=f'{rdelta.years} y and {rdelta.months} months')
                else:
                    st.text(f"Contract expires: None")
                if df_t['Date of last contract extension'].isnull().iloc[1]:
                    st.text(f"Date of\nlast contract extension: None")
                else:
                    st.text(
                        f"Date of last\ncontract extension: {df_t_t.loc['Date of last contract extension'][1]}")
                if df_t['Contract option'].isnull().iloc[1]:
                    st.text(f"Contract option: None")
                else:
                    st.text(
                        f"Contract option: {df_t_t.loc['Contract option'][1]}")

            with col3:
                if os.path.exists(f"seriea_loghi\\{df_t_t.loc['Current club'][1]}.png"):
                    st.text(
                        f"Current Club: {df_t_t.loc['Current club'][1]}")
                    st.image(
                        f"seriea_loghi\\{df_t_t.loc['Current club'][1]}.png")
                    st.text(f"Joined on : {df_t_t.loc['Joined'][1]}")
                    if not df_t['On loan from'].isnull().iloc[1]:
                        st.text(
                            f"On loan from: {df_t_t.loc['On loan from'][1]}")
                        st.image(
                            f"seriea_loghi\\{df_t_t.loc['On loan from'][1]}.png")
                else:
                    st.text(
                        f"Current Club: {df_t_t.loc['Current club'][1]}")
                    st.image(
                        "seriea_loghi\\blank.png")


else:
    st.markdown(
        """
        <style>
        u {
            text-decoration: underline;
            text-decoration-color: #fa4d00;
            }
        </style>
        ### Welcome to the Player Scouting App!</u> \n
        ##### With this application you have the ability to scout the most similar players compared to the player given in input.\
        Similarity is calculated using cosine distance.\
        The search can be refined by choosing various metrics to filter on, such as age, market value, and preferred foot.\
        One can also choose from which categories of players to search and whether to search only for players with expiring contracts. \n
        ##### There is Cluster_Analysis page where the clusters and the methodology used are described, both for defining the similarity metric and for constructing the clusters \n
        ##### To start, use the sidebar on the left to choose number of result  that will be shown and click on "RUN" button.
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