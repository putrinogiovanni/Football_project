import streamlit as st
import base64


# Page config
st.set_page_config(
    page_title="Scouting App",
    layout="wide"
)

st.title("Clustering and Recommendation - Analysis")


# App description
st.markdown(
    """
    ## **:red[Recommendation system]**\n
    ### The most popular Euclidean distance and Manhattan distance are two examples of distance measures that can be used to determine how similar two points are to one another. However, given the real-world dataset of football players who play a variety of roles and have a wide range of statistical output, they would not be the right metrics for this issue. Euclidean distance may not accurately indicate the degree of similarity between two vectors when working with high-dimensional data. This issue can be solved with the use of the cosine similarity metric.\n
    #### **:orange[Cosine Similarity]**: The cosine similarity index calculates how similar two vectors in an inner product space are to one another. It establishes whether two vectors are roughly pointing in the same direction by calculating the cosine of the angle between them. Its value falls between -1 and 1, with 1 denoting perfect similarity and -1 perfect dissimilarity.
    """)

st.image('sim_2.png')

st.markdown(
    """
    ## **:red[Cluster creation]**\n
    ### For the clusters creation we relied on the Bayesian-Gaussian-Mixture Model. We decided to choose this model because compared to other clustering models, such as the K-Means model, it provides a probability of belonging or not belonging to a certain cluster. In case you want to learn more about the technical work behind it see this link https://github.com/putrinogiovanni/Football_project/blob/main/Clustering_and_scraping/final.ipynb . These are the results obtained:\n
    """)

st.markdown(""" #### **:blue[Defenders Cluster]**
""")
col1, col2 = st.columns(2)

with col1:
    st.write('')
    st.write('')
    st.write('')
    st.write('')
    st.write('')
    st.write('')
    st.write('')
    st.image('data/weight_d.png', use_column_width=True)

with col2:
    st.image('cluster_dif.png',  use_column_width=True)


st.markdown("""1. In the first cluster we find defenders with a high number of duels, related to a high value of cautions. One can clearly see how offensive type statistics have particularly low values for these players. It is therefore expected that they are the players destined to stop the action. Indeed, in this cluster we find players such as ***:orange[Bremer]***, ***:orange[Chris Smalling]***, and ***:orange[Nikola Maksimovic]***.

2. In the second cluster we can see values similar to the third cluster with higher values, however, regarding duels of play and lower dribbling. Good values regarding physical metrics. These are players who play a role on the wing but with less offensive characteristics than in the third cluster. We find in this cluster players such as ***:orange[Marusic]***, ***:orange[De Sciglio]*** and ***:orange[Elseid Hysaj]***. 

3. To the third cluster belong players who present important values for Lateral_P90 balls, statistics related to running and distance and we find interesting values for crosses. Thus, defenders who play on the wing who make a good number of dribbles and crosses will belong to this cluster. Defenders such as for example ***:orange[Federico Dimarco], ***:orange[Álvaro Odriozola]***, ***:orange[Alex Sandro]***, ***:orange[Cristiano Biraghi]*** and ***:orange[Theo Hernández]*** are found in this cluster.

4. Players with fairly high values on Distance_TIP_90 and key passes belong to the fourth cluster. We can see that compared to the other clusters they present a lower number of duels and fouls made. The numbers on aerial duels and recovered balls are slightly higher than the other defenders. This is interesting, as they have good numbers on recovered balls but relatively few duels made. One might infer that these are players who therefore present good field placement. This suggests to us that in this cluster we go to find players who usually play the classic role of central defender. Indeed, we find among these players such as ***:orange[Bonucci]***, ***:orange[Skriniar]***, ***:orange[Milenkovic]***, and ***:orange[De Vrij]***.""")

st.markdown(""" #### **:blue[Midfielders Cluster]**
""")
col1, col2 = st.columns(2)

with col1:
    st.write('')
    st.write('')
    st.write('')
    st.write('')
    st.write('')
    st.write('')
    st.write('')
    st.image('data/weight_c.png', use_column_width=True)

with col2:
    st.image('cluster_cent.png',  use_column_width=True)


st.markdown("""1. In the first cluster we find midfielders with important levels regarding typically offensive metrics and with high numbers of key passes received. They therefore provide more contribution in the finalization phase. Among them we find players such as ***:orange[Milinkovic-Savic]***, ***:orange[Zaniolo]***, ***:orange[Pasalic]***, and ***:orange[McKennie]***.

2. In the second cluster we can see similar values to the first cluster. Thus, we have quite high values regarding offensive metrics but compared to the first cluster we have more balls recovered and higher values regarding defensive physical metrics (OTIP). Duels are mostly carried out in the offensive half of the field . In addition we have higher values regarding crosses. Among the clusters the players in this one have the highest number of cut backs. Players such as ***:orange[Gaetano Castrovilli]***, ***:orange[Henrikh Mkhitaryan]***, ***:orange[Brahim Díaz]***, ***:orange[Ivan Perisic]*** are found in this cluster. 

3. To the third cluster belong players with the highest value of stolen balls compared to all. There are lower average values of duels than in the first two clusters but these are mostly done in the defensive half of the field. There is also an important difference between the physical metrics in offense and defense. Thus we have in this cluster more defensive midfielders. One finds for example ***:orange[Lucas Torreira]***, ***:orange[Gary Medel]***, ***:orange[Milan Badelj]***.

4. Belonging to the fourth cluster are players who make many key passes, many third passes (the pass before the assist) and triangulations. The game duels are mainly developed in the defensive half of the field, where they manage to recover a good number of balls. They then distribute the ball within the team. Within this cluster are players such as ***:orange[Sofyan Amrabat]***, ***:orange[Marcelo Brozovic]***, ***:orange[Fabián Ruiz]*** and ***:orange[Manuel Locatelli]***""")


st.markdown(""" #### **:blue[Strikers Cluster]**
""")
col1, col2 = st.columns(2)

with col1:
    st.write('')
    st.write('')
    st.write('')
    st.write('')
    st.write('')
    st.write('')
    st.write('')
    st.image('data/weight_a.png', use_column_width=True)

with col2:
    st.image('cluster_att.png',  use_column_width=True)


st.markdown("""1. In the first cluster we find strikers with important levels of dueling and physical OTIP metrics (when the opponent has the ball). These are attackers who also receive a good number of balls. Thus, one can find players who fight a lot and play mainly on the central zone. For example, we have ***:orange[Ciro Immobile]***, ***:orange[David Okereke]***, and ***:orange[Kevin Lasagna]***.

2.  In the second cluster we can see interesting values regarding triangulations, side balls and key passes. A high number of dribbles, crosses and cut backs. They are therefore the attackers who to a greater extent provide assists. They also have good numbers in total shots but it is interesting to note that they rarely go for headers. In this cluster we find ***:orange[Paulo Dybala]***, ***:orange[Lorenzo Insigne]***, ***:orange[Rafael Leão]*** and ***:orange[Domenico Berardi]***. 

3. To the third cluster belong the classic forwards. So many passes received and so many shots, soaring over the other clusters for headers. The classic number 9. We find in this cluster players such as ***:orange[Edin Dzeko]***, ***:orange[Zlatan Ibrahimovic]***, ***:orange[Gianluca Scamacca]***, ***:orange[Antonio Sanabria]***.

4. This cluster turns out to be similar to the first one in some aspects. We find the highest number of duels among all clusters, with values on shots slightly lower than in the first one. The values on aerial duels and the low values on TIP physical metrics are interesting. We find in this cluster players such as ***:orange[Mattia Destro]***, ***:orange[Manolo Gabbiadini]***, ***:orange[Fabio Quagliarella]***, ***:orange[Beto]***""")
