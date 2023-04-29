import streamlit as st

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


st.set_page_config(
    page_title='WNBA Player Analysis App',
    page_icon=":basketball:",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None)

plt.style.use('fivethirtyeight')

COLORS = {
    'ATL': ['#4891ce', '#e3173e'],
    'CHA': ['#235985', '#e0623f'],
    'CHI': ['#4d90cd', '#ffd520'],
    'CLE': ['#c1c9ce', '#ffffff'],
    'CON': ['#002d62', '#bf2f38'],
    'DAL': ['#0d2240', '#c4d600'],
    'DET': ['#296bb1', '#da354f'],
    'HOU': ['#bd2c45', '#18467f'],
    'IND': ['#002d62', '#e03a3e'],
    'LVA': ['#c3002f', '#d1d1d1'],
    'LAS': ['#552583', '#fdb927'],
    'MIA': ['#b03e40', '#e8a04c'],
    'MIN': ['#005083', '#00a94f'],
    'NYL': ['#86cebc', '#d1d1d1'],
    'ORL': ['#397eb3', '#c4ccce'],
    'PHO': ['#e56020', '#603cbc'],
    'POR': ['#a45857', '#ccab54'],
    'SAC': ['#373b8f', '#bc2c47'],
    'SAN': ['#c6ccd0', '#ffffff'],
    'SEA': ['#2c5235', '#fee11a'],
    'TUL': ['#f3bb52', '#b42b37'],
    'UTA': ['#2c696c', '#b04c3b'],
    'WAS': ['#e03a3e', '#18467f'],
    'None': ['#a8a8a8', '#ffffff']
}

TEAMS = {
    'ATL': 1611661330,
    'CHA': 1611661314,
    'CHI': 1611661329,
    'CLE': 1611661315,
    'CON': 1611661323,
    'DAL': 1611661321,
    'DET': 1611661321,
    'HOU': 1611661316,
    'IND': 1611661325,
    'LVA': 1611661319,
    'LAS': 1611661320,
    'MIA': 1611661326,
    'MIN': 1611661324,
    'NYL': 1611661313,
    'ORL': 1611661323,
    'PHO': 1611661317,
    'POR': 1611661327,
    'SAC': 1611661318,
    'SAN': 1611661319,
    'SEA': 1611661328,
    'TUL': 1611661321,
    'UTA': 1611661319,
    'WAS': 1611661322
}

data = pd.read_parquet('app_data.parquet')

player_data = pd.read_parquet('wnba_player_data_updated.parquet')
player_data = player_data.drop_duplicates(subset='player_name')
records = player_data.filter(['player_id', 'player_name']).sort_values(
    by='player_name').to_dict('records')

first_players = [
    {'player_id': 200671, 'player_name': 'Seimone Augustus'},
    {'player_id': 1627668, 'player_name': 'Breanna Stewart'},
    {'player_id': 201496, 'player_name': 'Candace Parker'},
    {'player_id': 100940, 'player_name': 'Diana Taurasi'},
    {'player_id': 100720, 'player_name': 'Sue Bird'}
]
for i in first_players:
    records.insert(0, records.pop(records.index(i)))

with st.sidebar:
    st.image(
        "logo.png",
        use_column_width=True)
    with st.form('Form1'):
        selection = st.selectbox(
            'Select a Player', options=records,
            format_func=lambda record: f'{record["player_name"]}'
        )
        player = selection.get('player_id')
        start_y, end_y = st.slider(
            'Select a range of years', 1997, 2021, (1997, 2021))
        submitted = st.form_submit_button('Run')

    with st.expander("Metric Glossary*"):
        st.markdown(
            """
            <style>
            u {
                text-decoration: underline;
                text-decoration-color: #fa4d00;
                }
            m {
                font-size: 14px;
                }
            </style>
            <u>**Points Per Shot (PPS):**</u> The amount of points scored per shot
            *<m>150 total points on 100 total shots = 1.5 PPS</m>*
            ---
            <u>**Expected Points Per Shot (xPPS):**</u> The expected points per shot given the model's predicted 
            make probability multiplied by the proposed point value of a shot (2 or 3)
            *<m>2-pointer with a make probability of .60 = 1.2 xPTS, 3-pointer with a make probability of .30 = 0.9 xPTS
            (total xPTS / total shots = xPPS)</m>*
            ---
            <u>**Points Per Shot Over Expected (PPSOE):**</u> A measure of how well a player over or underperforms
            their expectation
            *<m>PPS - xPPS = PPSOE (made 2PT with a make prob. of .60, missed 3PT with a make prob. of .30
            = 1 PPS, 2.1 xPTS, -1.1 PPSOE. Averaged across all shot attempts)</m>*
            ---
            <u>**Field Goal Percent Over Expected (FGOE):**</u> An additional measure of how well a player over or underperforms
            their expectation based on shooting percentage. It is the difference between observed FG% and the mean
            of predicted make probabilities
            *<m>A successful field goal with a make probability of 0.50 = 50% FGOE, an unsuccessful field goal with
            a make probability of 0.20 = -20% FGOE
            (Averaged across all shot attempts)</m>*
            """,
            unsafe_allow_html=True
        )

    with st.expander("Prominent WNBA Rule Changes"):
        st.markdown(
            """
            <style>
            u {
                text-decoration: underline;
                text-decoration-color: #fa4d00;
                }
            </style>
            <u>**1997-2003:**</u>
            <m>*3PT distance, 19'9"*</m><br />
            <m>*Shot clock, 30s*</m><br />
            <m>*Two 20-min halves*</m>
            ---
            <u>**2004-2005:**</u> 
            
            <m>*3PT distance, 20'6.5"*</m><br />
            <m>*Shot clock, 30s*</m><br />
            <m>*Two 20-min halves*</m>
            ---
            <u>**2006-2012:**</u> 
            
            <m>*3PT distance, 20'6.5"*</m><br />
            <m>*Shot clock, 24s*</m><br />
            <m>*Four 10-min quarters*</m>
            ---
            <u>**2013-2021:**</u> 
            
            <m>*3PT distance, 22'1.75"*</m><br />
            <m>*Shot clock, 24s*</m><br />
            <m>*Four 10-min quarters*</m>
            """,
            unsafe_allow_html=True
        )
    with st.expander("Additional Info"):
        st.markdown(
            """
            <style>
            m {
                font-size: 14px;
                }
            </style>
            After rigorous testing, the model is an LGBM with default parameters 
            (sometimes simplicity is effective!) It uses the following features:
            <m>*Shot distance, Shot type (jump shot, fadeaway, etc.), X location, Y location, Time elapsed since tip (s), 
            Shooter's career regular season games played, Shooter's position (G, F, or C), Whether or not the shooter is playing at home,
            Whether or not the shot was a buzzer beater (<1 second remaining in quarter or half), Whether or not the
            game was played in "The Bubble" (2020), and which era the shot occured in (6 binned eras from '97-'21)*</m>
            The model was calibrated using Leave-One-Season-Out (LOSO) cross-validation, a technique where every season is used as
            a holdout set. That is, for each of the 25 available seasons (1997-2021), we exclude one season, train the model on 
            the other 24 seasons, and then compare the model’s predictions in the excluded holdout season to what actually happened in that season. 
            Various metrics are logged for each of the 25 holdout seasons and are ultimately averaged. If the model is well calibrated, we would expect that, 
            for example, 50 percent of shots with a make probability of 50 percent would be successful.
            """,
            unsafe_allow_html=True
        )

st.title('WNBA Player Analysis App')
if not submitted:

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
        st.image('wnba.png', width=900)

    with col3:
        st.write(' ')

else:
    player_data = player_data.loc[(player_data.player_id == player)]

    if player_data.team_abbreviation.isnull().iloc[0]:
        player_data.team_abbreviation = 'None'

    if start_y < player_data['from_year'].iloc[0].astype(int):
        s = player_data['from_year'].iloc[0].astype(int)
    else:
        s = start_y

    if end_y > player_data['to_year'].iloc[0].astype(int):
        e = player_data['to_year'].iloc[0].astype(int)
    else:
        e = end_y

    df = (data
          .loc[
              (data.year >= s) &
              (data.year <= e) &
              (data.player_id == player)
          ].copy()
          )

    if len(df) == 0:
        st.error(
            f'Oops! The selected player ({selection.get("player_name")}) did not play in '
            f'the selected time period ({start_y}-{end_y}). '
            'Please try a different configuration.'
        )
        st.stop()

    df_l = data.loc[
        (data.year >= s) &
        (data.year <= e)
    ].copy()

    col1, col2, col3, col4, col5 = st.columns([1, 1, 0.33, 0.33, 0.33])

    with col1:
        st.image(player_data.headshot_url.iloc[0], width=290)

    with col2:
        if 'Michelle Campbell' in player_data['player_name'].iloc[0]:
            st.text(
                "Name: Michelle Campbell"
            )
        else:
            st.text(
                f"Name: {player_data['player_name'].iloc[0]}"
            )
        if player_data.team_city.isnull().iloc[0]:
            st.text(
                "Team: None"
            )
        else:
            st.text(
                f"Team: {player_data['team_city'].iloc[0]} {player_data['team_name'].iloc[0]}"
            )
        st.text(
            f"Position: {player_data['position_initials'].iloc[0]}"
        )
        st.text(
            f"Height: {player_data['height'].iloc[0]}"
        )
        st.text(
            f"Weight (lbs): {player_data['weight'].iloc[0].astype(int)}"
        )
        st.text(
            f"Age, Yrs Exp: {player_data['age'].iloc[0]}, {player_data['season_exp'].iloc[0]} "
            f"({player_data['from_year'].iloc[0].astype(int)}-"
            f"{player_data['to_year'].iloc[0].astype(int)})"
        )
        if player_data.draft_year.iloc[0] == 'Undrafted':
            st.text(
                "Drafted: Undrafted"
            )
        elif player_data.draft_round.isnull().iloc[0]:
            st.text(
                f"Drafted: {player_data['draft_year'].iloc[0]}"
            )
        else:
            st.text(
                f"Drafted: {player_data['draft_year'].iloc[0]}, Round "
                f"{player_data['draft_round'].iloc[0]}, Pick {player_data['draft_number'].iloc[0]}"
            )
        st.text(
            f"Affiliations: {player_data['last_affiliation'].iloc[0]}"
        )

    with col3:
        if s == e:
            st.text(f'    {s},')
        else:
            st.text(f'    {s}-{e},')

        st.metric(
            label="FG%",
            value=round(df.shot_made_flag.mean() * 100, 1),
            delta=round((df.shot_made_flag.mean() -
                        df_l.shot_made_flag.mean()) * 100, 1)
        )

        st.metric(
            label="PPS*",
            value=round(df.outcome.sum() / df.shot_made_flag.count(), 2),
            delta=round(
                (df.outcome.sum() / df.shot_made_flag.count()) -
                (df_l.outcome.sum() / df_l.shot_made_flag.count()), 2
            )
        )

    with col4:
        st.text(f'{df.game_id.nunique()} GP')
        if len(df.loc[df['value'] == 3]) > 0:
            st.metric(
                label="3PT%",
                value=round(
                    df.loc[df['value'] == 3].shot_made_flag.mean() * 100, 1),
                delta=round(
                    (df
                     .loc[df['value'] == 3]
                     .shot_made_flag
                     .mean()
                     ) * 100 -
                    (df_l
                     .loc[df_l['value'] == 3]
                     .shot_made_flag
                     .mean()
                     ) * 100, 1
                )
            )
        else:
            st.metric(
                label="3PT%",
                value="-",
                delta="-",
                delta_color="off"
            )
        st.metric(
            label="xPPS*",
            value=round((df.value * df.pred_make).sum() /
                        df.shot_made_flag.count(), 2),
            delta=round(
                ((df.value * df.pred_make).sum() / df.shot_made_flag.count()) -
                ((df_l.value * df_l.pred_make).sum() /
                 df_l.shot_made_flag.count()), 2
            )
        )
    with col5:
        st.markdown(
            """
            <style>
            a {
                vertical-align: 13px;
            }
            </style>
            <a>
            <span style="color:#4da84b; font-style:italic; font-size:16px;">+</span>
            <span style="color:#FAFAFA; font-style:italic; font-size:14px;">/</span>
            <span style="color:#ec4239; font-style:italic; font-size:16px;">-</span>
            <span style="color:#FAFAFA; font-style:italic; font-size:14px;">Lg. Avg.</span>
            </a>
            """,
            unsafe_allow_html=True
        )

        st.metric(
            label="FGOE*",
            value=round(
                (df.shot_made_flag.mean() - df.pred_make.mean()) * 100, 1
            ),
            delta=round(
                (df.shot_made_flag.mean() - df.pred_make.mean()) * 100 -
                (df_l.shot_made_flag.mean() - df_l.pred_make.mean()) * 100, 1
            )
        )

        st.metric(
            label="PPSOE*",
            value=round(
                (df.outcome.sum() / df.shot_made_flag.count()) -
                ((df.value * df.pred_make).sum() / df.shot_made_flag.count()), 2
            ),
            delta=round(
                ((df.outcome.sum() / df.shot_made_flag.count()) -
                 ((df.value * df.pred_make).sum() / df.shot_made_flag.count())) -
                ((df_l.outcome.sum() / df_l.shot_made_flag.count()) -
                 ((df_l.value * df_l.pred_make).sum() / df_l.shot_made_flag.count())), 2
            )
        )

    col1, col2 = st.columns([1, 2])

    with col1:
        viz = (df
               .loc[df.shot_zone_basic != 'Backcourt']
               .groupby('shot_zone_basic')
               .agg({
                   'shot_made_flag': ['mean', 'count'],
                   'pred_make': 'mean'
               })
               )
        viz.columns = viz.columns.to_series().apply('_'.join)
        viz = (viz
               .sort_values(by='shot_made_flag_mean', ascending=False)
               .reset_index()
               )
        viz.shot_made_flag_mean = viz.shot_made_flag_mean * 100
        viz.pred_make_mean = viz.pred_make_mean * 100

        st.header("")
        fig, ax = plt.subplots()
        ax.set_facecolor(color='#0E1117')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.grid(zorder=0, alpha=0.8, color='#31333F')
        for i in ['left', 'right', 'top', 'bottom']:
            ax.spines[i].set_visible(False)

        sns.barplot(
            data=viz,
            x='shot_made_flag_mean',
            y='shot_zone_basic',
            palette=player_data.team_abbreviation.map(
                {k: v[0] for (k, v) in COLORS.items()})
        )

        ex_vals = viz.pred_make_mean.values
        lg_vals = (df_l
                   .loc[df_l.shot_zone_basic.isin(list(viz.shot_zone_basic))]
                   .groupby('shot_zone_basic')[['shot_made_flag']]
                   .mean()
                   .reindex(list(viz.shot_zone_basic))
                   .values
                   )
        lg_vals = [i*100 for i in lg_vals]

        zone = viz.shot_zone_basic.values
        vals = viz.shot_made_flag_mean.values
        counts = viz.shot_made_flag_count.values
        for i, (z, v, c) in enumerate(zip(zone, vals, counts)):
            if player_data.team_abbreviation.iloc[0] in ['NYL', 'CLE', 'SAN', 'PHO', 'HOU', 'TUL'] and v > 0:
                text_color = 'black'
            else:
                text_color = 'white'
            if (len(z) > 10) & (len(z) <= 15):
                z = '\n'.join(z.split(" ", 1))
                ax.text(
                    1, i+0.25, str(z) + ' ('+str(c)+')',
                    color=text_color, weight='bold', fontsize=12
                )
            elif (len(z) > 15) & (len(z) <= 19):
                z = ' '.join(z.split(" ", 2)[:2]) + \
                    '\n' + ' '.join(z.split(" ", 2)[2:])
                ax.text(
                    1, i+0.25, str(z) + ' ('+str(c)+')',
                    color=text_color, weight='bold', fontsize=12
                )
            elif len(z) > 19:
                z = ' '.join(z.split(" ", 3)[:3]) + \
                    '\n' + ' '.join(z.split(" ", 3)[3:])
                ax.text(
                    1, i+0.25, str(z) + ' ('+str(c)+')',
                    color=text_color, weight='bold', fontsize=12
                )
            else:
                ax.text(
                    1, i+0.075, str(z) + ' ('+str(c)+')',
                    color=text_color, weight='bold', fontsize=12
                )

        bar_w = [p.get_width() for p in ax.patches]
        bar_h = [p.get_height() for p in ax.patches]
        for i, (x, y, xx, v) in enumerate(zip(bar_w, bar_h, ex_vals, lg_vals)):
            line1 = plt.vlines(
                x=v,
                ymin=(i+(y/2)-0.01),
                ymax=(i-(y/2)),
                color=player_data.team_abbreviation.map(
                    {k: v[-1] for (k, v) in COLORS.items()}),
                linestyle='dotted',
                zorder=10,
                label='League Avg.'
            )
            line2 = plt.vlines(
                x=xx,
                ymin=(i+(y/2)-0.01),
                ymax=(i-(y/2)),
                color=player_data.team_abbreviation.map(
                    {k: v[-1] for (k, v) in COLORS.items()}),
                linestyle='solid',
                zorder=10,
                label='Expectation'
            )

        ax.set_yticks([])
        plt.legend(
            handles=[line1, line2], labelcolor='linecolor',
            facecolor='#0E1117', loc='lower right'
        ).get_frame().set_edgecolor('#0E1117')
        plt.xlabel('')
        plt.ylabel('')
        plt.title('FG% by Zone', color='white', fontsize=18)
        plt.tight_layout()
        plt.tick_params(axis='x', which='major', labelsize=16)
        st.pyplot(fig, facecolor='#0E1117', edgecolor='#0E1117')

        viz = (df
               .groupby('action_type').agg({
                   'shot_made_flag': ['mean', 'count'],
                   'pred_make': 'mean'
               })
               )
        viz.columns = viz.columns.to_series().apply('_'.join)
        viz = (viz
               .sort_values(by='shot_made_flag_count', ascending=False)
               .reset_index().head(5)
               .sort_values(by='shot_made_flag_mean', ascending=False)
               )
        viz.shot_made_flag_mean = viz.shot_made_flag_mean * 100
        viz.pred_make_mean = viz.pred_make_mean * 100

        st.header("")
        fig, ax = plt.subplots()
        ax.set_facecolor(color='#0E1117')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.grid(zorder=0, alpha=0.8, color='#31333F')
        for i in ['left', 'right', 'top', 'bottom']:
            ax.spines[i].set_visible(False)

        sns.barplot(
            data=viz,
            x='shot_made_flag_mean',
            y='action_type',
            palette=player_data.team_abbreviation.map(
                {k: v[0] for (k, v) in COLORS.items()})
        )

        ex_vals = viz.pred_make_mean.values
        lg_vals = (df_l
                   .loc[df_l.action_type.isin(list(viz.action_type))]
                   .groupby('action_type')[['shot_made_flag']]
                   .mean()
                   .reindex(list(viz.action_type))
                   .values
                   )
        lg_vals = [i*100 for i in lg_vals]

        actions = viz.action_type.values
        vals = viz.shot_made_flag_mean.values
        counts = viz.shot_made_flag_count.values
        for i, (a, v, c) in enumerate(zip(actions, vals, counts)):
            if player_data.team_abbreviation.iloc[0] in ['NYL', 'CLE', 'SAN', 'PHO', 'HOU', 'TUL'] and v > 0:
                text_color = 'black'
            else:
                text_color = 'white'
            if (len(a) > 10) & (len(a) < 20):
                a = '\n'.join(a.split(" ", 1))
                ax.text(
                    1, i+0.2, str(a) + ' ('+str(c)+')',
                    color=text_color, weight='bold', fontsize=12
                )
            elif len(a) > 20:
                a = ' '.join(a.split(" ", 2)[:2]) + \
                    '\n' + ' '.join(a.split(" ", 2)[2:])
                ax.text(
                    1, i+0.2, str(a) + ' ('+str(c)+')',
                    color=text_color, weight='bold', fontsize=12
                )
            else:
                ax.text(
                    1, i+0.05, str(a) + ' ('+str(c)+')',
                    color=text_color, weight='bold', fontsize=12
                )

        bar_w = [p.get_width() for p in ax.patches]
        bar_h = [p.get_height() for p in ax.patches]
        for i, (x, y, xx, v) in enumerate(zip(bar_w, bar_h, ex_vals, lg_vals)):
            line1 = plt.vlines(
                x=v,
                ymin=(i+(y/2)-0.01),
                ymax=(i-(y/2)),
                color=player_data.team_abbreviation.map(
                    {k: v[-1] for (k, v) in COLORS.items()}),
                linestyle=(0, (1, 1)),
                zorder=10,
                label='League Avg.'
            )
            line2 = plt.vlines(
                x=xx,
                ymin=(i+(y/2)-0.01),
                ymax=(i-(y/2)),
                color=player_data.team_abbreviation.map(
                    {k: v[-1] for (k, v) in COLORS.items()}),
                linestyle='solid',
                zorder=10,
                label='Expectation'
            )
        ax.set_yticks([])
        plt.legend(
            handles=[line1, line2], labelcolor='linecolor',
            facecolor='#0E1117', loc='lower right'
        ).get_frame().set_edgecolor('#0E1117')
        plt.xlabel('')
        plt.ylabel('')
        plt.title('FG% by Most Common Shot Types', color='white', fontsize=18)
        plt.tick_params(axis='x', which='major', labelsize=16)
        plt.tight_layout()
        st.pyplot(fig, facecolor='#0E1117', edgecolor='#0E1117')

    with col2:
        fig, ax = plt.subplots()
        fig = shot_chart(df_l, df)
        if (player_data['to_year'].iloc[0].astype(int) <= 2012) and (player_data['to_year'].iloc[0].astype(int) > 2003):
            draw_court(outer_lines=False, color='white', end_year=2012)
        elif player_data['to_year'].iloc[0].astype(int) <= 2003:
            draw_court(outer_lines=False, color='white', end_year=2003)
        else:
            draw_court(outer_lines=False, color='white', end_year=end_y)
        ax.set_facecolor(color='#0E1117')
        st.pyplot(fig, facecolor='#0E1117', edgecolor='#0E1117')

    viz = (data
           .loc[data.player_id == player]
           .groupby('gp').agg({'shot_made_flag': 'mean', 'pred_make': 'mean'})
           .reset_index()
           )
    viz.pred_make = viz.pred_make * 100
    viz.shot_made_flag = viz.shot_made_flag * 100

    lg_vals = (data
               .loc[data.gp <= viz.gp.max()]
               .groupby('gp')
               .agg({'shot_made_flag': 'mean', 'pred_make': 'mean'})
               .reset_index()
               )
    lg_vals.shot_made_flag = lg_vals.shot_made_flag * 100

    if viz.gp.max() > 6:
        r = round(viz.gp.max() * .075)
    else:
        r = np.ceil(viz.gp.max() * .075).astype(int)
    if viz.gp.max() <= 1:
        st.markdown(
            """
            #### This player only played one career game. As a result, they have no career progression chart.
            """
        )
    else:
        fig, ax = plt.subplots(figsize=(12, 3))
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.grid(zorder=0, alpha=0.6, color='#31333F')
        for i in ['left', 'right', 'top', 'bottom']:
            ax.spines[i].set_visible(False)
        line1 = sns.lineplot(
            x=viz.gp, y=viz.shot_made_flag.rolling(r).mean(), linewidth=2,
            color=player_data.team_abbreviation.map(
                {k: v[0] for (k, v) in COLORS.items()}).iloc[0],
            zorder=3, label='Field Goal %'
        )
        line2 = sns.lineplot(
            x=viz.gp, y=viz.pred_make.rolling(r).mean(), linewidth=2,
            color=player_data.team_abbreviation.map(
                {k: v[-1] for (k, v) in COLORS.items()}).iloc[0],
            zorder=2, label='Expectation'
        )
        line3 = sns.lineplot(
            x=lg_vals.gp, y=lg_vals.shot_made_flag.rolling(r).mean(), linewidth=2, alpha=0.85,
            color='lightgray', linestyle='dotted', zorder=1, label='League Avg.'
        )
        ax.fill_between(
            viz.gp,
            viz.shot_made_flag.rolling(r).mean(),
            viz.pred_make.rolling(r).mean(),
            where=viz.shot_made_flag.rolling(
                r).mean() > viz.pred_make.rolling(r).mean(),
            color=player_data.team_abbreviation.map(
                {k: v[0] for (k, v) in COLORS.items()}).iloc[0],
            alpha=0.3, interpolate=True
        )
        ax.fill_between(
            viz.gp,
            viz.shot_made_flag.rolling(r).mean(),
            viz.pred_make.rolling(r).mean(),
            where=viz.shot_made_flag.rolling(
                r).mean() < viz.pred_make.rolling(r).mean(),
            color=player_data.team_abbreviation.map(
                {k: v[-1] for (k, v) in COLORS.items()}).iloc[0],
            alpha=0.3, interpolate=True
        )
        plt.xlabel('Career Games Played', color='white', fontsize=14)
        plt.ylabel('')
        plt.legend(
            labelcolor='linecolor', facecolor='#0E1117', ncol=3,
            prop={'size': 10}
        ).get_frame().set_edgecolor('#0E1117')
        ax.set_facecolor(color='#0E1117')
        plt.tick_params(axis='both', which='major', labelsize=10)
        plt.title('Career Progression', fontsize=16, color='white')
        st.pyplot(fig, facecolor='#0E1117', edgecolor='#0E1117')

footer = """
    <style>
    footer {visibility: hidden;}
    MainMenu {visibility: hidden;}
    
    # footer:hover,  footer:active {
    #     color: #fa4d00;
    #     background-color: transparent;
    #     text-decoration: underline;
    #     transition: 400ms ease 0s;
    # }
    footer:after {
        content:'Created by Max Bolger'; 
        visibility: visible;
        display: block;
        position: relative;
        padding: 5px;
        top: 2px;
    }
    </style>
    """
st.markdown(footer, unsafe_allow_html=True)
