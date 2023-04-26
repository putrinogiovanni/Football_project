import streamlit as st
import base64


# Page config
st.set_page_config(
    page_title="Passing Style Analyser",
    page_icon="⚽️",
    layout="wide"
)

st.image("imgs/sics_soccerment_logos.png", width=450)

LOGO_IMAGE = "imgs/propic_erasmo_circle.png"
st.markdown(
    """
    <style>
    .container {
        display: flex;
    }
    .logo-text {
        font-weight: 50 !important;
        font-size: 30px !important;
        color: #008080 !important;
        padding-top: 15px !important;
        padding-left: 20px !important;
    }
    .logo-img {
        float:right;
        width: 85px;
        height: 85px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    f"""
    <div class="container">
        <img class="logo-img" src="data:image/png;base64,{base64.b64encode(open(LOGO_IMAGE, "rb").read()).decode()}">
        <p class="logo-text">Erasmo Purificato</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("Passing Style Analyser - Serie A 2021/22")


# App description
st.markdown(
    """
    With this application, you can analyse the passing style of each Serie A 2021/22 team.

    The two pages available in the sidebar are described below.

    ## Full Pitch & Field Tilt Networks
    
    After selected a **single matchday** or a **range of matchdays**, it is possible to analyse:
    * a single team,
    * two teams, or
    * all the 20 Serie A teams,
    by viewing their **passing network** in the **most used formation** for the selected matchdays, either visualizing the **full-pitch** or **field-tilt** passing network.

    Additionally, the user can select the number of minimum passes to be displayed in the passing networks (Note that for multiple matchdays, this value is multiplied by the number of selected matchdays).

    ## Match Status Networks

    After selected a **single matchday** or a **range of matchdays**, and a **team**, it is possible to analyse the full-pitch passing network for each **match status** (i.e. winning, drawing, losing) and view their barycenter in the "passing" scenario.

    Additionally, the user can decide whether or not to keep the goalkeeper in the barycenter computation, and select the number of minimum passes to be displayed in the passing networks (Note that in this case, for multiple matchdays, this value is **NOT** multiplied by the number of selected matchdays).

    """)