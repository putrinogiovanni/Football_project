import streamlit as st
import base64

st.markdown("""| Metric                    | Description                                                                             |
|---------------------------|-----------------------------------------------------------------------------------------|
| _p90                      | mins played adjusted (90 min.)                                                          |
| _p100                     | possession adjusted (100 touches)                                                       |
| OTIP                      | Team in Possession                                                                      |
| TIP                       | Opponent Team In Possesion                                                              |
| Count High Acceleration   | Discrete activity exceeding 3 m/s^2                                                     |
| Count High Deceleration   | Discrete activity under -3m/s^2                                                         |
| Count HSR                 | Discrete activity between 20 and 25 km/h.  The activity needs to last for at least 0.7s |
| Count Medium Acceleration | Discrete activity between 1.5 and 3 m/s^2                                               |
| Count Medium Deceleration | Discrete activity between -1.5 and -3 m/s^2                                             |
| Count Sprint              | Discrete activity exceeding 25km/h. The activity needs to last for at least 0.7s        |
| HI Distance               | Distance covered above 20 km/h                                                          |
| HSR Distance              | Distance covered between 20 and 25 km/h                                                 |
| Cross                     | Pass made from side zone in the last 30m towards the penalty area                       |
| Cut Back                  | Backward pass to a partner who is coming on the run                                     |
| Third pass                | Key pass before an assit                                                                |
| Shots inside              | Shot inside the box                                                                     |
| Shots outside             | Shot outside the box                                                                    |
| Forward cross             | Side pass that bypasses the defensive line. Is always a forward pass                    |""")
