# Import libraries
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.colors import to_rgba
import matplotlib.patheffects as path_effects
from mplsoccer.pitch import VerticalPitch


# Define constants
MAX_LINE_WIDTH_SINGLE = 11
MAX_MARKER_SIZE_SINGLE = 1000
MAX_LINE_WIDTH_TWO = 8
MAX_MARKER_SIZE_TWO = 800
MAX_LINE_WIDTH_ALL = 18
MAX_MARKER_SIZE_ALL = 7500
MAX_LINE_WIDTH_STATUS = 8
MAX_MARKER_SIZE_STATUS = 1000
XSHIFT_SINGLE = 1.5
YSHIFT_SINGLE = 1.5
XSHIFT_TWO = 1.5
YSHIFT_TWO = 1.5
XSHIFT_ALL = 1.5
YSHIFT_ALL = 1.5
TRASPARENT = True
COMET = True
ZORDER_PASS_LINES = 2
ALPHA_START = 0.0001
ALPHA_END = 0.8


# Define procedures
def compute_mins_per_lineup(team_name, matchday_list, teams_lineups):
    mins_lineups = {}
    for i in range(min(matchday_list)-1, max(matchday_list)):
        lups = teams_lineups[team_name]["lineups"]
        mins = teams_lineups[team_name]["mins_start_lineup"]
        if lups[i] in mins_lineups.keys():
            mins_lineups[lups[i]]["tot_mins"] = mins_lineups[lups[i]
                                                             ]["tot_mins"] + mins[i]
            mins_lineups[lups[i]]["matchdays"].append(i+1)
        else:
            mins_lineups[lups[i]] = {}
            mins_lineups[lups[i]]["tot_mins"] = mins[i]
            mins_lineups[lups[i]]["matchdays"] = []
            mins_lineups[lups[i]]["matchdays"].append(i+1)

    return mins_lineups


def create_df_passes_touches(df_select, team, matchday, teams_lineups, pitch_zone):
    df_passes = df_select[(df_select.type_id == 1) & (
        df_select.outcome == 1) & ~df_select.free_kick_taken & ~df_select.corner_taken]
    df_passes = df_passes[df_passes["pass_recipient"].notna()]
    df_passes["player_id"] = df_passes["player_id"].astype(int)
    df_passes["pass_recipient_id"] = df_passes["pass_recipient_id"].astype(int)
    mins_filter = teams_lineups[team]["mins_start_lineup"][matchday-1]
    df_passes = df_passes[df_passes.dec_time < mins_filter]
    df_passes = df_passes[df_passes["player_start_pos"].notna()]
    df_passes = df_passes[df_passes["pass_recip_start_pos"].notna()]
    df_passes["player_start_pos"] = df_passes["player_start_pos"].astype(int)
    df_passes["pass_recip_start_pos"] = df_passes["pass_recip_start_pos"].astype(
        int)

    df_touches = df_select[df_select.type_id.isin(
        [1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 41, 42, 50, 54, 61, 73, 74])]
    df_touches = df_touches.drop(
        df_touches[(df_touches.type_id == 4) & (df_touches.outcome == 0)].index)
    df_touches = df_touches[df_touches.dec_time < mins_filter]
    df_touches = df_touches[df_touches["player_start_pos"].notna()]
    df_touches["player_start_pos"] = df_touches["player_start_pos"].astype(int)

    if pitch_zone == "field_tilt":
        df_passes = df_passes[(df_passes.x > 66.5) & (df_passes.end_x > 66.5)]
        df_touches = df_touches[(df_touches.x > 66.5)
                                & (df_touches.end_x < 66.5)]

    return df_passes, df_touches


# DataFrame players single matchday
def create_df_players_single_matchday(df_passes, df_touches):
    df_passes_grouped = df_passes.groupby("player").agg(
        {"x": ["mean"], "y": ["mean", "count"], "xA": ["sum"]})
    df_passes_grouped.columns = ["avg_x", "avg_y", "pass_count", "xA"]
    df_touches_grouped = df_touches.groupby("player").agg({"x": ["count"]})
    df_touches_grouped.columns = ["touches_count"]
    df_players = df_passes_grouped.merge(
        df_touches_grouped, left_index=True, right_index=True)
    df_players["pass_T50"] = df_players["pass_count"] / \
        (df_players["touches_count"] / 50)
    df_players["xA_T50"] = df_players["xA"] / \
        (df_players["touches_count"] / 50)

    return df_players


# DataFrame players multiple matchdays
def create_df_players_multiple_matchdays(df_passes_concat, df_touches_concat):
    df_passes_tot = df_passes_concat.groupby("player_start_pos").agg(
        {"x": ["mean"], "y": ["mean", "count"], "xA": ["sum"]})
    df_passes_tot.columns = ["avg_x", "avg_y", "pass_count", "xA"]

    df_touches_tot = df_touches_concat.groupby(
        ["player_start_pos"]).agg({"x": ["count"]})
    df_touches_tot.columns = ["touches_count"]

    df_players_tot = df_passes_tot.merge(
        df_touches_tot, left_index=True, right_index=True)
    df_players_tot["pass_T50"] = df_players_tot["pass_count"] / \
        (df_players_tot["touches_count"] / 50)
    df_players_tot["xA_T50"] = df_players_tot["xA"] / \
        (df_players_tot["touches_count"] / 50)

    return df_players_tot


# DataFrame pass_between single matchday
def create_df_pass_between_single_matchday(df_passes, df_players, filter_passes_unit):
    df_pass_between = df_passes.groupby(
        ["player", "pass_recipient"]).timestamp.count().reset_index()
    df_pass_between.rename(
        {"timestamp": "pass_between_count"}, axis=1, inplace=True)
    df_pass_between = df_pass_between[df_pass_between.pass_between_count >=
                                      filter_passes_unit]
    df_pass_between = df_pass_between.merge(
        df_players, left_on="player", right_index=True)
    df_pass_between = df_pass_between.merge(
        df_players, left_on="pass_recipient", right_index=True, suffixes=["", "_end"])
    df_pass_between = df_pass_between.drop(
        ["pass_count_end", "xA_end", "touches_count_end", "pass_T50_end", "xA_T50_end"], axis=1)

    return df_pass_between


# DataFrame pass_between multiple matchdays
def create_df_pass_between_multiple_matchdays(df_passes_concat, df_players_tot, filter_passes):
    df_pass_between_tot = df_passes_concat.groupby(
        ["player_start_pos", "pass_recip_start_pos"]).timestamp.count().reset_index()
    df_pass_between_tot.rename({"player_start_pos": "passer", "pass_recip_start_pos": "recipient",
                               "timestamp": "pass_between_count"}, axis=1, inplace=True)
    df_pass_between_tot = df_pass_between_tot[df_pass_between_tot.pass_between_count >= filter_passes]
    df_pass_between_tot = df_pass_between_tot.merge(
        df_players_tot, left_on="passer", right_index=True)
    df_pass_between_tot = df_pass_between_tot.merge(
        df_players_tot, left_on="recipient", right_index=True, suffixes=["", "_end"])
    df_pass_between_tot.drop(["pass_count_end", "xA_end", "touches_count_end",
                             "pass_T50_end", "xA_T50_end"], axis=1, inplace=True)

    return df_pass_between_tot


# Plot single matchday single team
def plot_single_matchday_single_team(df_soccment, team, matchday, teams_lineups, pitch_zone, filter_passes_unit):

    # Create vars for visualization
    df_select = df_soccment[(df_soccment.matchday == matchday) & (
        df_soccment.team == team)]
    df_passes, df_touches = create_df_passes_touches(
        df_select, team, matchday, teams_lineups, pitch_zone)
    df_players = create_df_players_single_matchday(df_passes, df_touches)
    df_pass_between = create_df_pass_between_single_matchday(
        df_passes, df_players, filter_passes_unit)

    # Set properties for plotting the network
    df_pass_between["line_width"] = (df_pass_between.pass_between_count /
                                     df_pass_between.pass_between_count.max() * MAX_LINE_WIDTH_SINGLE)
    pass_count_max = df_players.pass_T50.max()
    df_players["marker_size"] = (
        df_players.pass_T50 / pass_count_max * MAX_MARKER_SIZE_SINGLE)

    # Setup the pitch
    pitch = VerticalPitch(pitch_type="opta", pitch_color="#122c3d", line_color="#cfcfcf", positional=True, positional_color="#cfcfcf",
                          positional_linestyle="--", positional_linewidth=1, positional_zorder=1, line_alpha=0.9, goal_alpha=1)
    fig, ax = pitch.draw(
        figsize=(8, 8.5), constrained_layout=True, tight_layout=True)
    fig.set_facecolor("#122c3d")

    # Insert pass lines
    for row in df_pass_between.itertuples():
        line_color = "azure"

        diff_x = row.avg_x - row.avg_x_end
        diff_y = row.avg_y - row.avg_y_end
        if diff_x < diff_y:
            if abs(diff_x) < abs(diff_y):
                pass_line = pitch.lines(row.avg_x + XSHIFT_SINGLE, row.avg_y, row.avg_x_end + XSHIFT_SINGLE, row.avg_y_end, lw=row.line_width,
                                        transparent=TRASPARENT, comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, ax=ax, zorder=ZORDER_PASS_LINES)
            elif abs(diff_x) > abs(diff_y):
                pass_line = pitch.lines(row.avg_x, row.avg_y + YSHIFT_SINGLE, row.avg_x_end, row.avg_y_end + YSHIFT_SINGLE, lw=row.line_width,
                                        transparent=TRASPARENT, comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, ax=ax, zorder=ZORDER_PASS_LINES)
        elif diff_x > diff_y:
            if abs(diff_x) < abs(diff_y):
                pass_line = pitch.lines(row.avg_x - XSHIFT_SINGLE, row.avg_y, row.avg_x_end - XSHIFT_SINGLE, row.avg_y_end, lw=row.line_width,
                                        transparent=TRASPARENT, comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, ax=ax, zorder=ZORDER_PASS_LINES)
            elif abs(diff_x) > abs(diff_y):
                pass_line = pitch.lines(row.avg_x, row.avg_y - YSHIFT_SINGLE, row.avg_x_end, row.avg_y_end - YSHIFT_SINGLE, lw=row.line_width,
                                        transparent=TRASPARENT, comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, ax=ax, zorder=ZORDER_PASS_LINES)
        elif diff_x == diff_y:
            if diff_x < 0:
                pass_line = pitch.lines(row.avg_x + XSHIFT_SINGLE, row.avg_y, row.avg_x_end + XSHIFT_SINGLE, row.avg_y_end, lw=row.line_width,
                                        transparent=TRASPARENT, comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, ax=ax, zorder=ZORDER_PASS_LINES)
            else:
                pass_line = pitch.lines(row.avg_x, row.avg_y - YSHIFT_SINGLE, row.avg_x_end, row.avg_y_end - YSHIFT_SINGLE, lw=row.line_width,
                                        transparent=TRASPARENT, comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, ax=ax, zorder=ZORDER_PASS_LINES)

    # Insert players
    pass_nodes = pitch.scatter(df_players.avg_x, df_players.avg_y, s=df_players.marker_size,
                               edgecolors="azure", linewidth=1, c=df_players.xA_T50, cmap="viridis", ax=ax, zorder=3)

    # Annotate scatter
    for p in df_players.itertuples():
        if len(p.Index.split()) > 1:
            name = p.Index.split()[0][0] + ". " + " ".join(p.Index.split()[1:])
        else:
            name = p.Index
        if p.avg_x <= 50:
            text = pitch.annotate(name, (p.avg_x - 2.5, p.avg_y), c="white",
                                  va="center", ha="center", size=9.5, weight="bold", ax=ax)
        else:
            text = pitch.annotate(name, (p.avg_x + 2.5, p.avg_y), c="white",
                                  va="center", ha="center", size=9.5, weight="bold", ax=ax)
        plt.setp(text, path_effects=[path_effects.withStroke(
            linewidth=2, foreground="black")])

    # Show legends
    cbar = plt.colorbar(pass_nodes, shrink=0.5, pad=0.01, location="left")
    cbar.ax.set_title("Expected\nAssist\nT50",
                      color="white", fontsize=10, pad=11)
    cbar_yticks = plt.getp(cbar.ax.axes, "yticklabels")
    plt.setp(cbar_yticks, color="white")
    cbar.ax.yaxis.set_tick_params(color="white", labelsize=9)
    pass_legend = plt.legend(*pass_nodes.legend_elements(prop="sizes", num=4, func=lambda s: (s*pass_count_max)/MAX_MARKER_SIZE_SINGLE, markeredgecolor="azure",
                             markerfacecolor="#122c3d"), fontsize=10, frameon=False, labelspacing=2.5, handletextpad=1.5, loc="center left", bbox_to_anchor=(0.98, 0.5), alignment="right")
    for text in pass_legend.get_texts():
        text.set_color("white")
        text.set_fontsize(9)
    pass_legend.set_title("Passes T50")
    pass_legend_title = pass_legend.get_title()
    pass_legend_title.set_color("white")
    pass_legend_title.set_size(10)

    # Title
    plt.suptitle(team, size=20, weight="bold", color="azure")
    plt.title("Matchday {}: Formation {} - {}'".format(matchday, teams_lineups[team]["lineups"][matchday-1], round(
        teams_lineups[team]["mins_start_lineup"][matchday-1])), size=14, color="azure")

    return fig


# Plot multple matchdays single team
def plot_multiple_matchdays_single_team(df_soccment, team, matchday_list, teams_lineups, pitch_zone, filter_passes_unit):
    # Most used formation in matchdays
    mins_lineups = compute_mins_per_lineup(team, matchday_list, teams_lineups)
    most_used_lineup = sorted(mins_lineups, key=lambda x: (
        mins_lineups[x]["tot_mins"]), reverse=True)[0]

    df_passes_list_per_matchday = []
    df_touches_list_per_matchday = []

    matchdays_lineup = mins_lineups[most_used_lineup]["matchdays"]
    for matchday in matchdays_lineup:
        # Create files for visualization
        df_select = df_soccment[(df_soccment.matchday == matchday) & (
            df_soccment.team == team)]
        df_passes, df_touches = create_df_passes_touches(
            df_select, team, matchday, teams_lineups, pitch_zone)
        df_passes_list_per_matchday.append(df_passes)
        df_touches_list_per_matchday.append(df_touches)
    df_passes_concat = pd.concat(
        df_passes_list_per_matchday, ignore_index=True)
    df_touches_concat = pd.concat(
        df_touches_list_per_matchday, ignore_index=True)

    df_players = create_df_players_multiple_matchdays(
        df_passes_concat, df_touches_concat)
    filter_passes = len(matchdays_lineup) * filter_passes_unit
    df_pass_between = create_df_pass_between_multiple_matchdays(
        df_passes_concat, df_players, filter_passes)

    # Set properties for plotting the network
    df_pass_between["line_width"] = (df_pass_between.pass_between_count /
                                     df_pass_between.pass_between_count.max() * MAX_LINE_WIDTH_SINGLE)
    pass_count_max = df_players.pass_T50.max()
    df_players["marker_size"] = (
        df_players.pass_T50 / pass_count_max * MAX_MARKER_SIZE_SINGLE)
    cmap = matplotlib.cm.get_cmap("viridis")
    norm_col = matplotlib.colors.Normalize(
        vmin=df_players.xA_T50.min(), vmax=df_players.xA_T50.max())

    # Setup the pitch
    pitch = VerticalPitch(pitch_type="opta", pitch_color="#122c3d", line_color="#cfcfcf", positional=True, positional_color="#cfcfcf",
                          positional_linestyle="--", positional_linewidth=1, positional_zorder=1, line_alpha=0.9, goal_alpha=1)

    mosaic_layout = [
        ["cm", "ns"],
        [".", "."],
        [team, team],
        [team+"_bar", team+"_bar"]
    ]
    fig, axs = plt.subplot_mosaic(mosaic_layout, layout="constrained", figsize=(
        6, 12), height_ratios=[1, 2, 50, 10])
    pitch.draw(ax=axs[team])

    fig.set_facecolor("#122c3d")

    # Insert pass lines
    for row in df_pass_between.itertuples():
        line_color = "azure"

        diff_x = row.avg_x - row.avg_x_end
        diff_y = row.avg_y - row.avg_y_end
        if diff_x < diff_y:
            if abs(diff_x) < abs(diff_y):
                pass_line = pitch.lines(row.avg_x + XSHIFT_SINGLE, row.avg_y, row.avg_x_end + XSHIFT_SINGLE, row.avg_y_end, lw=row.line_width,
                                        transparent=TRASPARENT, comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, ax=axs[team], zorder=ZORDER_PASS_LINES)
            elif abs(diff_x) > abs(diff_y):
                pass_line = pitch.lines(row.avg_x, row.avg_y + YSHIFT_SINGLE, row.avg_x_end, row.avg_y_end + YSHIFT_SINGLE, lw=row.line_width,
                                        transparent=TRASPARENT, comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, ax=axs[team], zorder=ZORDER_PASS_LINES)
        elif diff_x > diff_y:
            if abs(diff_x) < abs(diff_y):
                pass_line = pitch.lines(row.avg_x - XSHIFT_SINGLE, row.avg_y, row.avg_x_end - XSHIFT_SINGLE, row.avg_y_end, lw=row.line_width,
                                        transparent=TRASPARENT, comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, ax=axs[team], zorder=ZORDER_PASS_LINES)
            elif abs(diff_x) > abs(diff_y):
                pass_line = pitch.lines(row.avg_x, row.avg_y - YSHIFT_SINGLE, row.avg_x_end, row.avg_y_end - YSHIFT_SINGLE, lw=row.line_width,
                                        transparent=TRASPARENT, comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, ax=axs[team], zorder=ZORDER_PASS_LINES)
        elif diff_x == diff_y:
            if diff_x < 0:
                pass_line = pitch.lines(row.avg_x + XSHIFT_SINGLE, row.avg_y, row.avg_x_end + XSHIFT_SINGLE, row.avg_y_end, lw=row.line_width,
                                        transparent=TRASPARENT, comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, ax=axs[team], zorder=ZORDER_PASS_LINES)
            else:
                pass_line = pitch.lines(row.avg_x, row.avg_y - YSHIFT_SINGLE, row.avg_x_end, row.avg_y_end - YSHIFT_SINGLE, lw=row.line_width,
                                        transparent=TRASPARENT, comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, ax=axs[team], zorder=ZORDER_PASS_LINES)

    # Insert players
    pass_nodes = pitch.scatter(df_players.avg_x, df_players.avg_y, s=df_players.marker_size,
                               edgecolors="azure", linewidth=1, c=df_players.xA_T50, cmap="viridis", ax=axs[team], zorder=3)

    # Annotate scatter
    for p in df_players.itertuples():
        text = pitch.annotate(p.Index, xy=(p.avg_x, p.avg_y), c="white",
                              va="center", ha="center", size=9, weight="bold", ax=axs[team])
        plt.setp(text, path_effects=[path_effects.withStroke(
            linewidth=2, foreground="black")])

    # Axis title
    title_props = {"fontsize": 18, "fontweight": "bold", "color": "azure"}
    axs[team].set_title(team, fontdict=title_props)

    # Show legends
    cbar = matplotlib.colorbar.ColorbarBase(
        ax=axs["cm"], orientation="horizontal", cmap="viridis", norm=norm_col)
    cbar_title = cbar.ax.set_title(
        "Expected Assist T50 (xA_T50)", color="white", fontsize=10, pad=10)
    cbar_yticks = plt.getp(cbar.ax.axes, "xticklabels")
    plt.setp(cbar_yticks, color="white")
    cbar.ax.xaxis.set_tick_params(color="white", labelsize=9)

    pass_legend = axs["ns"].legend(*pass_nodes.legend_elements(prop="sizes", num=4, func=lambda s: (s*pass_count_max)/MAX_MARKER_SIZE_SINGLE, markeredgecolor="azure",
                                   markerfacecolor="#122c3d"), fontsize=10, frameon=False, labelspacing=2, handletextpad=1.2, loc="center", alignment="center", ncol=4, bbox_to_anchor=(0.5, 0.5))
    axs["ns"].axis("off")
    for text in pass_legend.get_texts():
        text.set_color("white")
        text.set_fontsize(9)
    pass_legend.set_title("Pass count T50")
    pass_legend_title = pass_legend.get_title()
    pass_legend_title.set_color("white")
    pass_legend_title.set_size(10)

    # Pitch title
    fig.suptitle("Passing networks for matchdays {}-{}\n".format(
        min(matchday_list), max(matchday_list)), size=18, color="azure")

    # Plot formations histogram
    mins_lineups = compute_mins_per_lineup(team, matchday_list, teams_lineups)
    most_used = sorted(mins_lineups, key=lambda x: (
        mins_lineups[x]["tot_mins"]), reverse=True)
    formations = list(mins_lineups.keys())[::-1]
    mins = [mins_lineups[k]["tot_mins"] for k in mins_lineups.keys()][::-1]
    axs[team+"_bar"].set_facecolor("#122c3d")
    axs[team+"_bar"].spines.top.set_visible(False)
    axs[team+"_bar"].spines.right.set_visible(False)
    axs[team+"_bar"].spines.bottom.set_color("azure")
    axs[team+"_bar"].spines.left.set_color("azure")

    barh = axs[team+"_bar"].barh(formations, mins, height=0.7, color=[
                                 "lightgreen" if form == most_used[0] else "azure" for form in formations])
    axs[team+"_bar"].set_title("Most used formation: {} ({}/{} games - {}')".format(most_used[0], len(mins_lineups[most_used[0]]
                               ["matchdays"]), len(matchday_list), int(mins_lineups[most_used[0]]["tot_mins"])), size=11, color="azure", loc="center")
    axs[team+"_bar"].set_ylabel("Formations", color="azure")
    axs[team+"_bar"].set_xlabel("Minutes played", color="azure")
    axs[team+"_bar"].tick_params(axis="x", color="azure")
    axs[team+"_bar"].tick_params(axis="y", color="azure")
    plt.setp(axs[team+"_bar"].get_xticklabels(), color="azure")
    plt.setp(axs[team+"_bar"].get_yticklabels(), color="azure")

    return fig


# Plot single matchday two teams
def plot_single_matchday_two_teams(df_soccment, team_list, matchday, teams_lineups, pitch_zone, filter_passes_unit):

    # Create vars for visualization
    df_players_list = []
    df_pass_between_list = []
    for team in team_list:
        df_select = df_soccment[(df_soccment.matchday == matchday) & (
            df_soccment.team == team)]
        df_passes, df_touches = create_df_passes_touches(
            df_select, team, matchday, teams_lineups, pitch_zone)
        df_players = create_df_players_single_matchday(df_passes, df_touches)
        df_pass_between = create_df_pass_between_single_matchday(
            df_passes, df_players, filter_passes_unit)
        df_players_list.append(df_players)
        df_pass_between_list.append(df_pass_between)

    # Properties for plotting the passing network
    df_players_list_concat = pd.concat(df_players_list, ignore_index=True)
    df_pass_between_list_concat = pd.concat(
        df_pass_between_list, ignore_index=True)
    cmap = matplotlib.cm.get_cmap("viridis")
    norm_col = matplotlib.colors.Normalize(
        vmin=df_players_list_concat.xA_T50.min(), vmax=df_players_list_concat.xA_T50.max())

    for i in range(len(team_list)):
        pass_between_count_max = df_pass_between_list_concat.pass_between_count.max()
        df_pass_between_list[i]["line_width"] = (
            df_pass_between_list[i].pass_between_count / pass_between_count_max * MAX_LINE_WIDTH_TWO)
        pass_count_max = df_players_list_concat.pass_count.max()
        if pitch_zone == "field_tilt":
            df_players_list[i]["marker_size"] = (
                df_players_list[i].pass_T50 / pass_count_max * MAX_MARKER_SIZE_TWO / 20)
        else:
            df_players_list[i]["marker_size"] = (
                df_players_list[i].pass_T50 / pass_count_max * MAX_MARKER_SIZE_TWO)

    # Plot pass networks
    pitch = VerticalPitch(pitch_type="opta", pitch_color="#122c3d", line_color="#cfcfcf", positional=True, positional_color="#cfcfcf",
                          positional_linestyle="--", positional_linewidth=1, positional_zorder=1, line_alpha=0.9, goal_alpha=0.9)

    mosaic_layout = [
        ["cm", "ns"],
        [".", "."],
        team_list
    ]
    fig, axs = plt.subplot_mosaic(
        mosaic_layout, layout="constrained", figsize=(9, 10), height_ratios=[1, 3, 50])
    fig.set_facecolor("#122c3d")

    for i in range(len(team_list)):
        pitch.draw(ax=axs[team_list[i]])

        # Insert pass lines
        for row in df_pass_between_list[i].itertuples():
            line_color = "azure"

            diff_x = row.avg_x - row.avg_x_end
            diff_y = row.avg_y - row.avg_y_end
            if diff_x < diff_y:
                if abs(diff_x) < abs(diff_y):
                    pass_line = pitch.lines(row.avg_x + XSHIFT_TWO, row.avg_y, row.avg_x_end + XSHIFT_TWO, row.avg_y_end, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, ax=axs[team_list[i]], zorder=ZORDER_PASS_LINES)
                elif abs(diff_x) > abs(diff_y):
                    pass_line = pitch.lines(row.avg_x, row.avg_y + YSHIFT_TWO, row.avg_x_end, row.avg_y_end + YSHIFT_TWO, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, ax=axs[team_list[i]], zorder=ZORDER_PASS_LINES)
            elif diff_x > diff_y:
                if abs(diff_x) < abs(diff_y):
                    pass_line = pitch.lines(row.avg_x - XSHIFT_TWO, row.avg_y, row.avg_x_end - XSHIFT_TWO, row.avg_y_end, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, ax=axs[team_list[i]], zorder=ZORDER_PASS_LINES)
                elif abs(diff_x) > abs(diff_y):
                    pass_line = pitch.lines(row.avg_x, row.avg_y - YSHIFT_TWO, row.avg_x_end, row.avg_y_end - YSHIFT_TWO, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, ax=axs[team_list[i]], zorder=ZORDER_PASS_LINES)
            elif diff_x == diff_y:
                if diff_x < 0:
                    pass_line = pitch.lines(row.avg_x + XSHIFT_TWO, row.avg_y, row.avg_x_end + XSHIFT_TWO, row.avg_y_end, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, ax=axs[team_list[i]], zorder=ZORDER_PASS_LINES)
                else:
                    pass_line = pitch.lines(row.avg_x, row.avg_y - YSHIFT_TWO, row.avg_x_end, row.avg_y_end - YSHIFT_TWO, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, ax=axs[team_list[i]], zorder=ZORDER_PASS_LINES)

        # Insert players
        pass_nodes = pitch.scatter(df_players_list[i].avg_x, df_players_list[i].avg_y, s=df_players_list[i].marker_size, edgecolors="azure",
                                   linewidth=1, c=df_players_list[i].xA_T50, cmap="viridis", norm=norm_col, zorder=3, ax=axs[team_list[i]])

        # Annotate scatter
        for p in df_players_list[i].itertuples():
            if len(p.Index.split()) > 1:
                name = p.Index.split()[0][0] + ". " + \
                    " ".join(p.Index.split()[1:])
            else:
                name = p.Index
            if p.avg_x <= 50:
                text = pitch.annotate(name, (p.avg_x - 2.5, p.avg_y), c="white",
                                      va="center", ha="center", size=9, weight="bold", ax=axs[team_list[i]])
            else:
                text = pitch.annotate(name, (p.avg_x + 2.5, p.avg_y), c="white",
                                      va="center", ha="center", size=9, weight="bold", ax=axs[team_list[i]])
            plt.setp(text, path_effects=[path_effects.withStroke(
                linewidth=2, foreground="black")])

        # Axis title
        title_props = {"fontsize": 17,
                       "fontweight": "normal", "color": "azure"}
        axs[team_list[i]].set_title(team_list[i], fontdict=title_props)

        axs[team_list[i]].text(75, -5, "Formation: {} ({}')".format(teams_lineups[team_list[i]]["lineups"][matchday-1],
                               round(teams_lineups[team_list[i]]["mins_start_lineup"][matchday-1])), size=14, color="azure")

    # Set figure title
    fig.suptitle("Passing networks for matchday {}\n".format(
        matchday), size=18, color="azure")

    # Plot colorbar
    cbar = matplotlib.colorbar.ColorbarBase(
        ax=axs["cm"], orientation="horizontal", cmap="viridis", norm=norm_col)
    cbar_title = cbar.ax.set_title(
        "Expected Assist T50 (xA_T50)", color="white", fontsize=10, pad=10)
    cbar_yticks = plt.getp(cbar.ax.axes, "xticklabels")
    plt.setp(cbar_yticks, color="white")
    cbar.ax.xaxis.set_tick_params(color="white", labelsize=9)

    # Plot marker legend
    pass_legend = axs["ns"].legend(*pass_nodes.legend_elements(prop="sizes", num=4, func=lambda s: (s*pass_count_max)/MAX_MARKER_SIZE_TWO, markeredgecolor="azure",
                                   markerfacecolor="#122c3d"), fontsize=10, frameon=False, labelspacing=2, handletextpad=1.2, loc="center", alignment="center", ncol=4, bbox_to_anchor=(0.5, 0.5))
    axs["ns"].axis("off")
    for text in pass_legend.get_texts():
        text.set_color("white")
        text.set_fontsize(9)
    pass_legend.set_title("Pass count T50")
    pass_legend_title = pass_legend.get_title()
    pass_legend_title.set_color("white")
    pass_legend_title.set_size(10)

    return fig

# Plot multple matchdays two teams


def plot_multiple_matchdays_two_teams(df_soccment, team_list, matchday_list, teams_lineups, pitch_zone, filter_passes_unit):

    # Create var for visualization
    df_players_list = []
    df_pass_between_list = []
    for team in team_list:
        mins_lineups = compute_mins_per_lineup(
            team, matchday_list, teams_lineups)
        most_used_lineup = sorted(mins_lineups, key=lambda x: (
            mins_lineups[x]["tot_mins"]), reverse=True)[0]

        df_passes_list_per_matchday = []
        df_touches_list_per_matchday = []

        matchdays_lineup = mins_lineups[most_used_lineup]["matchdays"]
        for matchday in matchdays_lineup:
            df_select = df_soccment[(df_soccment.matchday == matchday) & (
                df_soccment.team == team)]
            df_passes, df_touches = create_df_passes_touches(
                df_select, team, matchday, teams_lineups, pitch_zone)
            df_passes_list_per_matchday.append(df_passes)
            df_touches_list_per_matchday.append(df_touches)

        df_passes_concat = pd.concat(
            df_passes_list_per_matchday, ignore_index=True)
        df_touches_concat = pd.concat(
            df_touches_list_per_matchday, ignore_index=True)

        df_players = create_df_players_multiple_matchdays(
            df_passes_concat, df_touches_concat)
        filter_passes = len(matchdays_lineup) * filter_passes_unit
        df_pass_between = create_df_pass_between_multiple_matchdays(
            df_passes_concat, df_players, filter_passes)

        df_players_list.append(df_players)
        df_pass_between_list.append(df_pass_between)

    # Properties for plotting the passing network
    df_players_list_concat = pd.concat(df_players_list, ignore_index=True)
    df_pass_between_list_concat = pd.concat(
        df_pass_between_list, ignore_index=True)
    cmap = matplotlib.cm.get_cmap("viridis")
    norm_col = matplotlib.colors.Normalize(
        vmin=df_players_list_concat.xA_T50.min(), vmax=df_players_list_concat.xA_T50.max())

    for i in range(len(team_list)):
        pass_between_count_max = df_pass_between_list_concat.pass_between_count.max()
        df_pass_between_list[i]["line_width"] = (
            df_pass_between_list[i].pass_between_count / pass_between_count_max * MAX_LINE_WIDTH_TWO)
        pass_count_max = df_players_list_concat.pass_T50.max()
        df_players_list[i]["marker_size"] = (
            df_players_list[i].pass_T50 / pass_count_max * MAX_MARKER_SIZE_TWO)

    # Plot pass networks
    pitch = VerticalPitch(pitch_type="opta", pitch_color="#122c3d", line_color="#cfcfcf", positional=True, positional_color="#cfcfcf",
                          positional_linestyle="--", positional_linewidth=1, positional_zorder=1, line_alpha=0.9, goal_alpha=0.9)

    mosaic_layout = [
        ["cm", "ns"],
        [".", "."],
        team_list,
        [t+"_bar" for t in team_list]
    ]
    fig, axs = plt.subplot_mosaic(mosaic_layout, layout="constrained", figsize=(
        9, 10), height_ratios=[1, 5, 50, 10])
    fig.set_facecolor("#122c3d")

    for i in range(len(team_list)):
        pitch.draw(ax=axs[team_list[i]])

        # Insert pass lines
        for row in df_pass_between_list[i].itertuples():
            line_color = "azure"

            diff_x = row.avg_x - row.avg_x_end
            diff_y = row.avg_y - row.avg_y_end
            if diff_x < diff_y:
                if abs(diff_x) < abs(diff_y):
                    pass_line = pitch.lines(row.avg_x + XSHIFT_TWO, row.avg_y, row.avg_x_end + XSHIFT_TWO, row.avg_y_end, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, zorder=ZORDER_PASS_LINES, ax=axs[team_list[i]])
                elif abs(diff_x) > abs(diff_y):
                    pass_line = pitch.lines(row.avg_x, row.avg_y + YSHIFT_TWO, row.avg_x_end, row.avg_y_end + YSHIFT_TWO, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, zorder=ZORDER_PASS_LINES, ax=axs[team_list[i]])
            elif diff_x > diff_y:
                if abs(diff_x) < abs(diff_y):
                    pass_line = pitch.lines(row.avg_x - XSHIFT_TWO, row.avg_y, row.avg_x_end - XSHIFT_TWO, row.avg_y_end, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, zorder=ZORDER_PASS_LINES, ax=axs[team_list[i]])
                elif abs(diff_x) > abs(diff_y):
                    pass_line = pitch.lines(row.avg_x, row.avg_y - YSHIFT_TWO, row.avg_x_end, row.avg_y_end - YSHIFT_TWO, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, zorder=ZORDER_PASS_LINES, ax=axs[team_list[i]])
            elif diff_x == diff_y:
                if diff_x < 0:
                    pass_line = pitch.lines(row.avg_x + XSHIFT_TWO, row.avg_y, row.avg_x_end + XSHIFT_TWO, row.avg_y_end, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, zorder=ZORDER_PASS_LINES, ax=axs[team_list[i]])
                else:
                    pass_line = pitch.lines(row.avg_x, row.avg_y - YSHIFT_TWO, row.avg_x_end, row.avg_y_end - YSHIFT_TWO, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, zorder=ZORDER_PASS_LINES, ax=axs[team_list[i]])

        # Insert players
        pass_nodes = pitch.scatter(df_players_list[i].avg_x, df_players_list[i].avg_y, s=df_players_list[i].marker_size, edgecolors="azure",
                                   linewidth=1, c=df_players_list[i].xA_T50, cmap="viridis", norm=norm_col, zorder=3, ax=axs[team_list[i]])

        # Insert players annotations
        for p in df_players_list[i].itertuples():
            text = pitch.annotate(p.Index, xy=(p.avg_x, p.avg_y), c="white",
                                  va="center", ha="center", size=9, weight="bold", ax=axs[team_list[i]])
            plt.setp(text, path_effects=[path_effects.withStroke(
                linewidth=2, foreground="black")])

        # Axis title
        title_props = {"fontsize": 17,
                       "fontweight": "normal", "color": "azure"}
        axs[team_list[i]].set_title(team_list[i], fontdict=title_props)

        # Plot formations histogram
        mins_lineups = compute_mins_per_lineup(
            team_list[i], matchday_list, teams_lineups)
        most_used = sorted(mins_lineups, key=lambda x: (
            mins_lineups[x]["tot_mins"]), reverse=True)
        formations = list(mins_lineups.keys())[::-1]
        mins = [mins_lineups[k]["tot_mins"] for k in mins_lineups.keys()][::-1]
        axs[team_list[i]+"_bar"].set_facecolor("#122c3d")
        axs[team_list[i]+"_bar"].spines.top.set_visible(False)
        axs[team_list[i]+"_bar"].spines.right.set_visible(False)
        axs[team_list[i]+"_bar"].spines.bottom.set_color("azure")
        axs[team_list[i]+"_bar"].spines.left.set_color("azure")

        barh = axs[team_list[i]+"_bar"].barh(formations, mins, height=0.7, color=[
                                             "lightgreen" if form == most_used[0] else "azure" for form in formations])
        axs[team_list[i]+"_bar"].set_title("Most used formation: {} ({}/{} games - {}')".format(most_used[0], len(
            mins_lineups[most_used[0]]["matchdays"]), len(matchday_list), int(mins_lineups[most_used[0]]["tot_mins"])), size=11, color="azure", loc="center")
        axs[team_list[i]+"_bar"].set_ylabel("Formations", color="azure")
        axs[team_list[i]+"_bar"].set_xlabel("Minutes played", color="azure")
        axs[team_list[i]+"_bar"].tick_params(axis="x", color="azure")
        axs[team_list[i]+"_bar"].tick_params(axis="y", color="azure")
        plt.setp(axs[team_list[i]+"_bar"].get_xticklabels(), color="azure")
        plt.setp(axs[team_list[i]+"_bar"].get_yticklabels(), color="azure")

    # Set figure title
    fig.suptitle("Passing networks for matchdays {}-{}\n".format(
        min(matchday_list), max(matchday_list)), size=18, color="azure")

    # Plot colorbar
    cbar = matplotlib.colorbar.ColorbarBase(
        ax=axs["cm"], orientation="horizontal", cmap="viridis", norm=norm_col)
    cbar_title = cbar.ax.set_title(
        "Expected Assist T50 (xA_T50)", color="white", fontsize=10, pad=10)
    cbar_yticks = plt.getp(cbar.ax.axes, "xticklabels")
    plt.setp(cbar_yticks, color="white")
    cbar.ax.xaxis.set_tick_params(color="white", labelsize=9)

    # Plot marker legend
    pass_legend = axs["ns"].legend(*pass_nodes.legend_elements(prop="sizes", num=4, func=lambda s: (s*pass_count_max)/MAX_MARKER_SIZE_TWO, markeredgecolor="azure",
                                   markerfacecolor="#122c3d"), fontsize=10, frameon=False, labelspacing=2, handletextpad=1.2, loc="center", alignment="center", ncol=4, bbox_to_anchor=(0.5, 0.5))
    axs["ns"].axis("off")
    for text in pass_legend.get_texts():
        text.set_color("white")
        text.set_fontsize(9)
    pass_legend.set_title("Pass count T50")
    pass_legend_title = pass_legend.get_title()
    pass_legend_title.set_color("white")
    pass_legend_title.set_size(10)

    return fig


# Plot single matchday all teams
def plot_single_matchday_all_teams(df_soccment, team_list, matchday, teams_lineups, pitch_zone, filter_passes_unit):

    # Create vars for visualization
    df_players_list = []
    df_pass_between_list = []
    for team in team_list:
        df_select = df_soccment[(df_soccment.matchday == matchday) & (
            df_soccment.team == team)]
        df_passes, df_touches = create_df_passes_touches(
            df_select, team, matchday, teams_lineups, pitch_zone)
        df_players = create_df_players_single_matchday(df_passes, df_touches)
        df_pass_between = create_df_pass_between_single_matchday(
            df_passes, df_players, filter_passes_unit)
        df_players_list.append(df_players)
        df_pass_between_list.append(df_pass_between)

    # Properties for plotting the passing network
    df_players_list_concat = pd.concat(df_players_list, ignore_index=True)
    df_pass_between_list_concat = pd.concat(
        df_pass_between_list, ignore_index=True)
    cmap = matplotlib.cm.get_cmap("viridis")
    norm_col = matplotlib.colors.Normalize(
        vmin=df_players_list_concat.xA_T50.min(), vmax=df_players_list_concat.xA_T50.max())

    for i in range(len(team_list)):
        pass_between_count_max = df_pass_between_list_concat.pass_between_count.max()
        df_pass_between_list[i]["line_width"] = (
            df_pass_between_list[i].pass_between_count / pass_between_count_max * MAX_LINE_WIDTH_ALL)
        pass_count_max = df_players_list_concat.pass_count.max()
        if pitch_zone == "field_tilt":
            df_players_list[i]["marker_size"] = (
                df_players_list[i].pass_T50 / pass_count_max * MAX_MARKER_SIZE_ALL / 40)
        else:
            df_players_list[i]["marker_size"] = (
                df_players_list[i].pass_T50 / pass_count_max * MAX_MARKER_SIZE_ALL)

    # Plot pass networks
    pitch = VerticalPitch(pitch_type="opta", pitch_color="#122c3d", line_color="#cfcfcf", positional=True, positional_color="#cfcfcf",
                          positional_linestyle="--", positional_linewidth=1, positional_zorder=1, line_alpha=0.9, goal_alpha=0.9)

    mosaic_layout = [
        [".", "cm", ".", "ns", "."],
        [".", ".", ".", ".", "."],
        team_list[:5],
        team_list[5:10],
        team_list[10:15],
        team_list[15:],
    ]
    fig, axs = plt.subplot_mosaic(mosaic_layout, layout="constrained", figsize=(
        50, 75), height_ratios=[1, 2, 30, 30, 30, 30])
    fig.set_facecolor("#122c3d")

    for i in range(len(team_list)):
        pitch.draw(ax=axs[team_list[i]])

        # Insert pass lines
        for row in df_pass_between_list[i].itertuples():
            line_color = "azure"

            diff_x = row.avg_x - row.avg_x_end
            diff_y = row.avg_y - row.avg_y_end
            if diff_x < diff_y:
                if abs(diff_x) < abs(diff_y):
                    pass_line = pitch.lines(row.avg_x + XSHIFT_ALL, row.avg_y, row.avg_x_end + XSHIFT_ALL, row.avg_y_end, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, ax=axs[team_list[i]], zorder=ZORDER_PASS_LINES)
                elif abs(diff_x) > abs(diff_y):
                    pass_line = pitch.lines(row.avg_x, row.avg_y + YSHIFT_ALL, row.avg_x_end, row.avg_y_end + YSHIFT_ALL, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, ax=axs[team_list[i]], zorder=ZORDER_PASS_LINES)
            elif diff_x > diff_y:
                if abs(diff_x) < abs(diff_y):
                    pass_line = pitch.lines(row.avg_x - XSHIFT_ALL, row.avg_y, row.avg_x_end - XSHIFT_ALL, row.avg_y_end, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, ax=axs[team_list[i]], zorder=ZORDER_PASS_LINES)
                elif abs(diff_x) > abs(diff_y):
                    pass_line = pitch.lines(row.avg_x, row.avg_y - YSHIFT_ALL, row.avg_x_end, row.avg_y_end - YSHIFT_ALL, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, ax=axs[team_list[i]], zorder=ZORDER_PASS_LINES)
            elif diff_x == diff_y:
                if diff_x < 0:
                    pass_line = pitch.lines(row.avg_x + XSHIFT_ALL, row.avg_y, row.avg_x_end + XSHIFT_ALL, row.avg_y_end, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, ax=axs[team_list[i]], zorder=ZORDER_PASS_LINES)
                else:
                    pass_line = pitch.lines(row.avg_x, row.avg_y - YSHIFT_ALL, row.avg_x_end, row.avg_y_end - YSHIFT_ALL, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, ax=axs[team_list[i]], zorder=ZORDER_PASS_LINES)

        # Insert players
        pass_nodes = pitch.scatter(df_players_list[i].avg_x, df_players_list[i].avg_y, s=df_players_list[i].marker_size, edgecolors="azure",
                                   linewidth=1, c=df_players_list[i].xA_T50, cmap="viridis", norm=norm_col, zorder=3, ax=axs[team_list[i]])

        # Axis title
        title_props = {"fontsize": 45,
                       "fontweight": "normal", "color": "azure"}
        axs[team_list[i]].set_title(team_list[i], fontdict=title_props)

        axs[team_list[i]].text(75, -5, "Formation: {} ({}')".format(teams_lineups[team_list[i]]["lineups"][matchday-1],
                               round(teams_lineups[team_list[i]]["mins_start_lineup"][matchday-1])), size=35, color="azure")

    # Set figure title
    fig.suptitle("Passing networks for matchday {}\n".format(
        matchday), size=50, color="azure")

    # Plot colorbar
    cbar = matplotlib.colorbar.ColorbarBase(
        ax=axs["cm"], orientation="horizontal", cmap="viridis", norm=norm_col)
    cbar_title = cbar.ax.set_title(
        "Expected Assist T50 (xA_T50)", color="white", fontsize=35, pad=30)
    cbar_yticks = plt.getp(cbar.ax.axes, "xticklabels")
    plt.setp(cbar_yticks, color="white")
    cbar.ax.xaxis.set_tick_params(color="white", labelsize=30)

    # Plot marker legend
    pass_legend = axs["ns"].legend(*pass_nodes.legend_elements(prop="sizes", num=4, func=lambda s: (s*pass_count_max)/MAX_MARKER_SIZE_TWO, markeredgecolor="azure",
                                   markerfacecolor="#122c3d"), fontsize=25, frameon=False, labelspacing=1.5, handletextpad=0.5, loc="center", alignment="center", ncol=4, bbox_to_anchor=(0.5, 0.5))
    axs["ns"].axis("off")
    for text in pass_legend.get_texts():
        text.set_color("white")
        text.set_fontsize(30)
    pass_legend.set_title("Pass count T50")
    pass_legend_title = pass_legend.get_title()
    pass_legend_title.set_color("white")
    pass_legend_title.set_size(35)

    return fig


# Plot multiple matchdays all teams
def plot_multiple_matchdays_all_teams(df_soccment, team_list, matchday_list, teams_lineups, pitch_zone, filter_passes_unit):

    # Create var for visualization
    df_players_list = []
    df_pass_between_list = []
    for team in team_list:
        mins_lineups = compute_mins_per_lineup(
            team, matchday_list, teams_lineups)
        most_used_lineup = sorted(mins_lineups, key=lambda x: (
            mins_lineups[x]["tot_mins"]), reverse=True)[0]

        df_passes_list_per_matchday = []
        df_touches_list_per_matchday = []

        matchdays_lineup = mins_lineups[most_used_lineup]["matchdays"]
        for matchday in matchdays_lineup:
            df_select = df_soccment[(df_soccment.matchday == matchday) & (
                df_soccment.team == team)]
            df_passes, df_touches = create_df_passes_touches(
                df_select, team, matchday, teams_lineups, pitch_zone)
            df_passes_list_per_matchday.append(df_passes)
            df_touches_list_per_matchday.append(df_touches)

        df_passes_concat = pd.concat(
            df_passes_list_per_matchday, ignore_index=True)
        df_touches_concat = pd.concat(
            df_touches_list_per_matchday, ignore_index=True)

        df_players = create_df_players_multiple_matchdays(
            df_passes_concat, df_touches_concat)
        filter_passes = len(matchdays_lineup) * filter_passes_unit
        df_pass_between = create_df_pass_between_multiple_matchdays(
            df_passes_concat, df_players, filter_passes)

        df_players_list.append(df_players)
        df_pass_between_list.append(df_pass_between)

    # Properties for plotting the passing network
    df_players_list_concat = pd.concat(df_players_list, ignore_index=True)
    df_pass_between_list_concat = pd.concat(
        df_pass_between_list, ignore_index=True)
    cmap = matplotlib.cm.get_cmap("viridis")
    norm_col = matplotlib.colors.Normalize(
        vmin=df_players_list_concat.xA_T50.min(), vmax=df_players_list_concat.xA_T50.max())

    for i in range(len(team_list)):
        pass_between_count_max = df_pass_between_list_concat.pass_between_count.max()
        df_pass_between_list[i]["line_width"] = (
            df_pass_between_list[i].pass_between_count / pass_between_count_max * MAX_LINE_WIDTH_ALL)
        pass_count_max = df_players_list_concat.pass_T50.max()
        df_players_list[i]["marker_size"] = (
            df_players_list[i].pass_T50 / pass_count_max * MAX_MARKER_SIZE_ALL)

    # Plot pass networks
    pitch = VerticalPitch(pitch_type="opta", pitch_color="#122c3d", line_color="#cfcfcf", positional=True, positional_color="#cfcfcf",
                          positional_linestyle="--", positional_linewidth=1, positional_zorder=1, line_alpha=0.9, goal_alpha=0.9)

    mosaic_layout = [
        [".", "cm", ".", "ns", "."],
        [".", ".", ".", ".", "."],
        team_list[:5],
        team_list[5:10],
        team_list[10:15],
        team_list[15:],
    ]
    fig, axs = plt.subplot_mosaic(mosaic_layout, layout="constrained", figsize=(
        50, 75), height_ratios=[1, 2, 30, 30, 30, 30])
    fig.set_facecolor("#122c3d")

    for i in range(len(team_list)):
        pitch.draw(ax=axs[team_list[i]])

        # Insert pass lines
        for row in df_pass_between_list[i].itertuples():
            line_color = "azure"

            diff_x = row.avg_x - row.avg_x_end
            diff_y = row.avg_y - row.avg_y_end
            if diff_x < diff_y:
                if abs(diff_x) < abs(diff_y):
                    pass_line = pitch.lines(row.avg_x + XSHIFT_ALL, row.avg_y, row.avg_x_end + XSHIFT_ALL, row.avg_y_end, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, zorder=ZORDER_PASS_LINES, ax=axs[team_list[i]])
                elif abs(diff_x) > abs(diff_y):
                    pass_line = pitch.lines(row.avg_x, row.avg_y + YSHIFT_ALL, row.avg_x_end, row.avg_y_end + YSHIFT_ALL, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, zorder=ZORDER_PASS_LINES, ax=axs[team_list[i]])
            elif diff_x > diff_y:
                if abs(diff_x) < abs(diff_y):
                    pass_line = pitch.lines(row.avg_x - XSHIFT_ALL, row.avg_y, row.avg_x_end - XSHIFT_ALL, row.avg_y_end, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, zorder=ZORDER_PASS_LINES, ax=axs[team_list[i]])
                elif abs(diff_x) > abs(diff_y):
                    pass_line = pitch.lines(row.avg_x, row.avg_y - YSHIFT_ALL, row.avg_x_end, row.avg_y_end - YSHIFT_ALL, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, zorder=ZORDER_PASS_LINES, ax=axs[team_list[i]])
            elif diff_x == diff_y:
                if diff_x < 0:
                    pass_line = pitch.lines(row.avg_x + XSHIFT_ALL, row.avg_y, row.avg_x_end + XSHIFT_ALL, row.avg_y_end, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, zorder=ZORDER_PASS_LINES, ax=axs[team_list[i]])
                else:
                    pass_line = pitch.lines(row.avg_x, row.avg_y - YSHIFT_ALL, row.avg_x_end, row.avg_y_end - YSHIFT_ALL, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, zorder=ZORDER_PASS_LINES, ax=axs[team_list[i]])

        # Insert players
        pass_nodes = pitch.scatter(df_players_list[i].avg_x, df_players_list[i].avg_y, s=df_players_list[i].marker_size, edgecolors="azure",
                                   linewidth=1, c=df_players_list[i].xA_T50, cmap="viridis", norm=norm_col, zorder=3, ax=axs[team_list[i]])

        # Axis title
        title_props = {"fontsize": 45,
                       "fontweight": "normal", "color": "azure"}
        axs[team_list[i]].set_title(team_list[i], fontdict=title_props)

        mins_lineups = compute_mins_per_lineup(
            team_list[i], matchday_list, teams_lineups)
        most_used = sorted(mins_lineups, key=lambda x: (
            mins_lineups[x]["tot_mins"]), reverse=True)
        axs[team_list[i]].text(100, -8, "Most used formation: {}\n({}/{} games - {}')".format(most_used[0], len(
            mins_lineups[most_used[0]]["matchdays"]), len(matchday_list), int(mins_lineups[most_used[0]]["tot_mins"])), size=35, color="azure")

    # Set figure title
    fig.suptitle("Passing networks for matchdays {}-{}\n".format(
        min(matchday_list), max(matchday_list)), size=50, color="azure")

    # Plot colorbar
    cbar = matplotlib.colorbar.ColorbarBase(
        ax=axs["cm"], orientation="horizontal", cmap="viridis", norm=norm_col)
    cbar_title = cbar.ax.set_title(
        "Expected Assist T50 (xA_T50)", color="white", fontsize=35, pad=30)
    cbar_yticks = plt.getp(cbar.ax.axes, "xticklabels")
    plt.setp(cbar_yticks, color="white")
    cbar.ax.xaxis.set_tick_params(color="white", labelsize=30)

    # Plot marker legend
    pass_legend = axs["ns"].legend(*pass_nodes.legend_elements(prop="sizes", num=4, func=lambda s: (s*pass_count_max)/MAX_MARKER_SIZE_TWO, markeredgecolor="azure",
                                   markerfacecolor="#122c3d"), fontsize=25, frameon=False, labelspacing=1.5, handletextpad=0.7, loc="center", alignment="center", ncol=4, bbox_to_anchor=(0.5, 0.5))
    axs["ns"].axis("off")
    for text in pass_legend.get_texts():
        text.set_color("white")
        text.set_fontsize(30)
    pass_legend.set_title("Pass count T50")
    pass_legend_title = pass_legend.get_title()
    pass_legend_title.set_color("white")
    pass_legend_title.set_size(35)

    return fig


# Plot team info for match status page
def plot_team_match_status_formation_info(team, matchday_list, teams_match_status, teams_lineups):

    mosaic_layout = [
        ["status", "formations"]
    ]
    fig, axs = plt.subplot_mosaic(
        mosaic_layout, layout="constrained", figsize=(10, 4))
    fig.set_facecolor("#122c3d")

    # Plot match status distribution in matchday_list
    tot_played = 0.0
    tot_w = 0.0
    tot_d = 0.0
    tot_l = 0.0
    for matchday in matchday_list:
        matchday = str(matchday)
        tot_played = tot_played + teams_match_status[team][matchday][0]
        tot_w = tot_w + teams_match_status[team][matchday][1]
        tot_d = tot_d + teams_match_status[team][matchday][2]
        tot_l = tot_l + teams_match_status[team][matchday][3]
    axs["status"].set_facecolor("#122c3d")
    axs["status"].spines.top.set_visible(False)
    axs["status"].spines.right.set_visible(False)
    axs["status"].spines.bottom.set_color("azure")
    axs["status"].spines.left.set_color("azure")

    # y_shown = [tot_w/tot_played*100, tot_d/tot_played*100, tot_l/tot_played*100]
    y_shown = [tot_w, tot_d, tot_l]
    axs["status"].bar(["W", "D", "L"], y_shown, width=0.7, color="teal")
    axs["status"].set_title("Time per match status",
                            size=11, color="azure", loc="center")
    # axs["status"].set_ylabel("Percentage", color="azure")
    axs["status"].set_ylabel("Minutes played", color="azure")
    axs["status"].set_xlabel("Match status", color="azure")
    axs["status"].tick_params(axis="x", color="azure")
    axs["status"].tick_params(axis="y", color="azure")
    plt.setp(axs["status"].get_xticklabels(), color="azure")
    plt.setp(axs["status"].get_yticklabels(), color="azure")

    # Plot formations histogram
    mins_lineups = compute_mins_per_lineup(team, matchday_list, teams_lineups)
    # most_used = sorted(mins_lineups, key=lambda x: (mins_lineups[x]["tot_mins"]), reverse=True)
    formations = list(mins_lineups.keys())[::-1]
    mins = [mins_lineups[k]["tot_mins"] for k in mins_lineups.keys()][::-1]
    axs["formations"].set_facecolor("#122c3d")
    axs["formations"].spines.top.set_visible(False)
    axs["formations"].spines.right.set_visible(False)
    axs["formations"].spines.bottom.set_color("azure")
    axs["formations"].spines.left.set_color("azure")

    axs["formations"].barh(formations, mins, height=0.7, color="teal")
    axs["formations"].set_title(
        "Formations used", size=11, color="azure", loc="center")
    axs["formations"].set_ylabel("Formations", color="azure")
    axs["formations"].set_xlabel("Minutes played", color="azure")
    axs["formations"].tick_params(axis="x", color="azure")
    axs["formations"].tick_params(axis="y", color="azure")
    plt.setp(axs["formations"].get_xticklabels(), color="azure")
    plt.setp(axs["formations"].get_yticklabels(), color="azure")

    if len(matchday_list) == 1:
        fig.suptitle("Formations and match status info for {} in matchday {}\n".format(
            team, matchday_list[0]), size=15, color="azure")
    else:
        fig.suptitle("Formations and match status info for {} in matchdays {}-{}\n".format(
            team, min(matchday_list), max(matchday_list)), size=15, color="azure")

    return fig


# Plot passing networks per match status
def plot_match_status_networks(df_soccment, team, matchday_list, teams_lineups, filter_passes_unit, exclude_gk):

    df_passes_W_per_matchday = []
    df_touches_W_per_matchday = []
    df_passes_D_per_matchday = []
    df_touches_D_per_matchday = []
    df_passes_L_per_matchday = []
    df_touches_L_per_matchday = []

    for matchday in matchday_list:
        df_select = df_soccment[(df_soccment.matchday == matchday) & (
            df_soccment.team == team)]
        df_passes, df_touches = create_df_passes_touches(
            df_select, team, matchday, teams_lineups, "full")
        df_passes_W = df_passes[df_passes.match_status == "W"]
        df_passes_D = df_passes[df_passes.match_status == "D"]
        df_passes_L = df_passes[df_passes.match_status == "L"]
        df_touches_W = df_touches[df_touches.match_status == "W"]
        df_touches_D = df_touches[df_touches.match_status == "D"]
        df_touches_L = df_touches[df_touches.match_status == "L"]

        df_passes_W_per_matchday.append(df_passes_W)
        df_touches_W_per_matchday.append(df_touches_W)
        df_passes_D_per_matchday.append(df_passes_D)
        df_touches_D_per_matchday.append(df_touches_D)
        df_passes_L_per_matchday.append(df_passes_L)
        df_touches_L_per_matchday.append(df_touches_L)

    df_passes_W_concat = pd.concat(df_passes_W_per_matchday, ignore_index=True)
    df_touches_W_concat = pd.concat(
        df_touches_W_per_matchday, ignore_index=True)
    df_passes_D_concat = pd.concat(df_passes_D_per_matchday, ignore_index=True)
    df_touches_D_concat = pd.concat(
        df_touches_D_per_matchday, ignore_index=True)
    df_passes_L_concat = pd.concat(df_passes_L_per_matchday, ignore_index=True)
    df_touches_L_concat = pd.concat(
        df_touches_L_per_matchday, ignore_index=True)

    df_players_W = create_df_players_multiple_matchdays(
        df_passes_W_concat, df_touches_W_concat)
    df_players_D = create_df_players_multiple_matchdays(
        df_passes_D_concat, df_touches_D_concat)
    df_players_L = create_df_players_multiple_matchdays(
        df_passes_L_concat, df_touches_L_concat)

    # filter_passes = len(matchday_list) * filter_passes_unit
    filter_passes = filter_passes_unit
    df_pass_between_W = create_df_pass_between_multiple_matchdays(
        df_passes_W_concat, df_players_W, filter_passes)
    df_pass_between_D = create_df_pass_between_multiple_matchdays(
        df_passes_D_concat, df_players_D, filter_passes)
    df_pass_between_L = create_df_pass_between_multiple_matchdays(
        df_passes_L_concat, df_players_L, filter_passes)

    # Set properties for plotting the network
    df_pass_between_W["line_width"] = (
        df_pass_between_W.pass_between_count / df_pass_between_W.pass_between_count.max() * MAX_LINE_WIDTH_STATUS)
    pass_count_max = df_players_W.pass_T50.max()
    df_players_W["marker_size"] = (
        df_players_W.pass_T50 / pass_count_max * MAX_MARKER_SIZE_STATUS)
    df_pass_between_D["line_width"] = (
        df_pass_between_D.pass_between_count / df_pass_between_D.pass_between_count.max() * MAX_LINE_WIDTH_STATUS)
    pass_count_max = df_players_D.pass_T50.max()
    df_players_D["marker_size"] = (
        df_players_D.pass_T50 / pass_count_max * MAX_MARKER_SIZE_STATUS)
    df_pass_between_L["line_width"] = (
        df_pass_between_L.pass_between_count / df_pass_between_L.pass_between_count.max() * MAX_LINE_WIDTH_STATUS)
    pass_count_max = df_players_L.pass_T50.max()
    df_players_L["marker_size"] = (
        df_players_L.pass_T50 / pass_count_max * MAX_MARKER_SIZE_STATUS)

    # Create lists
    df_pass_between_list = [df_pass_between_W,
                            df_pass_between_D, df_pass_between_L]
    df_players_list = [df_players_W, df_players_D, df_players_L]

    # Visualization
    pitch = VerticalPitch(pitch_type="opta", pitch_color="grass", line_color="white",
                          stripe=True, positional=True, positional_linestyle="--", positional_linewidth=0.7)

    status_list = ["Winning", "Drawing", "Losing"]

    mosaic_layout = [
        status_list
    ]
    fig, axs = plt.subplot_mosaic(
        mosaic_layout, layout="constrained", figsize=(15, 10))
    fig.set_facecolor("#122c3d")

    for i in range(len(status_list)):
        pitch.draw(ax=axs[status_list[i]])

        # Insert pass lines
        for row in df_pass_between_list[i].itertuples():
            line_color = "azure"

            diff_x = row.avg_x - row.avg_x_end
            diff_y = row.avg_y - row.avg_y_end
            if diff_x < diff_y:
                if abs(diff_x) < abs(diff_y):
                    pass_line = pitch.lines(row.avg_x + XSHIFT_TWO, row.avg_y, row.avg_x_end + XSHIFT_TWO, row.avg_y_end, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, zorder=ZORDER_PASS_LINES, ax=axs[status_list[i]])
                elif abs(diff_x) > abs(diff_y):
                    pass_line = pitch.lines(row.avg_x, row.avg_y + YSHIFT_TWO, row.avg_x_end, row.avg_y_end + YSHIFT_TWO, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, zorder=ZORDER_PASS_LINES, ax=axs[status_list[i]])
            elif diff_x > diff_y:
                if abs(diff_x) < abs(diff_y):
                    pass_line = pitch.lines(row.avg_x - XSHIFT_TWO, row.avg_y, row.avg_x_end - XSHIFT_TWO, row.avg_y_end, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, zorder=ZORDER_PASS_LINES, ax=axs[status_list[i]])
                elif abs(diff_x) > abs(diff_y):
                    pass_line = pitch.lines(row.avg_x, row.avg_y - YSHIFT_TWO, row.avg_x_end, row.avg_y_end - YSHIFT_TWO, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, zorder=ZORDER_PASS_LINES, ax=axs[status_list[i]])
            elif diff_x == diff_y:
                if diff_x < 0:
                    pass_line = pitch.lines(row.avg_x + XSHIFT_TWO, row.avg_y, row.avg_x_end + XSHIFT_TWO, row.avg_y_end, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, zorder=ZORDER_PASS_LINES, ax=axs[status_list[i]])
                else:
                    pass_line = pitch.lines(row.avg_x, row.avg_y - YSHIFT_TWO, row.avg_x_end, row.avg_y_end - YSHIFT_TWO, lw=row.line_width, transparent=TRASPARENT,
                                            comet=COMET, color=line_color, alpha_start=ALPHA_START, alpha_end=ALPHA_END, zorder=ZORDER_PASS_LINES, ax=axs[status_list[i]])

        # Insert players
        pass_nodes = pitch.scatter(df_players_list[i].avg_x, df_players_list[i].avg_y, s=df_players_list[i].marker_size,
                                   edgecolors="azure", linewidth=1, color="teal", zorder=4, ax=axs[status_list[i]])

        # Compute barycenter
        if df_players_list[i].avg_x.any():
            df_tmp = df_players_list[i].copy()
            if exclude_gk:
                df_tmp.drop(index=1, inplace=True)
            max_x = max(df_tmp.avg_x)
            min_x = min(df_tmp.avg_x)
            bc_x = (max_x + min_x) / 2
            bc_line = pitch.lines(
                bc_x, 0, bc_x, 100, lw=3, color="orangered", zorder=3, ax=axs[status_list[i]])
            bc_value = pitch.annotate(str(round(bc_x, 1)) + " m", xy=(bc_x + 2, 2), c="orangered",
                                      va="center", ha="center", size=12, weight="bold", ax=axs[status_list[i]], zorder=5)
            plt.setp(bc_value, path_effects=[
                     path_effects.withStroke(linewidth=3, foreground="white")])

        # Insert players annotations
        for p in df_players_list[i].itertuples():
            text = pitch.annotate(p.Index, xy=(p.avg_x, p.avg_y), c="white", va="center",
                                  ha="center", size=9, weight="bold", ax=axs[status_list[i]])
            plt.setp(text, path_effects=[path_effects.withStroke(
                linewidth=2, foreground="black")], zorder=5)

        # Axis title
        title_props = {"fontsize": 17,
                       "fontweight": "normal", "color": "white"}
        axs[status_list[i]].set_title(status_list[i], fontdict=title_props)

    # Set figure title
    if len(matchday_list) == 1:
        fig.suptitle("Passing distribution and barycenter for {} in matchday {} (for each match status)".format(
            team, matchday_list[0]), size=20, color="white")
    else:
        fig.suptitle("Passing distribution and barycenter for {} in matchdays {}-{} (for each match status)".format(
            team, min(matchday_list), max(matchday_list)), size=20, color="white")

    return fig


def pizza_chart(params, value1, value2):
    baker = PyPizza(
        params=params,                  # list of parameters
        background_color="#EBEBE9",     # background color
        straight_line_color="#222222",  # color for straight lines
        straight_line_lw=1,             # linewidth for straight lines
        last_circle_lw=1,               # linewidth of last circle
        last_circle_color="#222222",    # color of last circle
        other_circle_ls="-.",           # linestyle for other circles
        other_circle_lw=1               # linewidth for other circles
    )

    # plot pizza
    fig, ax = baker.make_pizza(
        value1,                     # list of values
        compare_values=value2,    # comparison values
        figsize=(8, 8),             # adjust figsize according to your need
        kwargs_slices=dict(
            facecolor="blue", edgecolor="black",
            zorder=2, linewidth=1, alpha=0.5, label='Vlahovic'
        ),                          # values to be used when plotting slices
        kwargs_compare=dict(
            facecolor="red", edgecolor="black",
            zorder=2, linewidth=1, alpha=0.5, label='Lautaro'
        ),
        kwargs_params=dict(
            color="#000000", fontsize=12, va="center"
        ),                          # values to be used when adding parameter
        # values to be used when adding parameter-values labels
        kwargs_values=dict(fontsize=0),
        # values to be used when adding parameter-values labels
        kwargs_compare_values=dict(fontsize=0),
    )

    #plt.legend(bbox_to_anchor = (1.2, 1))

    return fig
#plt.savefig('pizza_example.png', bbox_inches = 'tight')
