# Import libraries
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.colors import to_rgba
import matplotlib.patheffects as path_effects
from mplsoccer.pitch import Pitch, VerticalPitch
from mplsoccer import PyPizza, Radar
from highlight_text import fig_text


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
    st.write("OK")
    #plt.legend(bbox_to_anchor = (1.2, 1))

    return fig
#plt.savefig('pizza_example.png', bbox_inches = 'tight')
