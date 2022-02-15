import altair as alt
import math
import os
import pandas as pd
import streamlit as st

st.set_page_config(
     page_title="NBA Stats for 2021-2022",
     page_icon="basketball",
     layout="wide",
     initial_sidebar_state="collapsed",
     menu_items={
         'Get Help': 'https://docs.streamlit.io/library/api-reference',
         'About': "This app shows the main statistics about the players of the season 2021-2022"
     }
 )

# Define function that loads the data and obtain new variables
@st.cache()
def load_data(nrows):  
    working_directory = os.getcwd()
    filename = '/Downloads/2021-2022_NBA_Player_Stats.csv' 
    data_df = pd.read_csv(working_directory + filename,
                          delimiter=";", 
                          encoding="latin-1", 
                          index_col=0)

    fgm = data_df.FGA - data_df.FG
    ftm = data_df.FTA - data_df.FT
    data_df.insert(29, 'FGM', fgm)
    data_df.insert(30, 'FTM', ftm)
    eff = data_df.PTS + data_df.TRB + data_df.AST + data_df.STL + data_df.BLK - data_df.FGM - data_df.FTM - data_df.TOV
    data_df.insert(31, 'EFF', eff)
    return data_df

# Title
st.title("NBA Stats 2021-2022")

# Load data
data_load_state = st.text("Loading data...")
raw_df = load_data(None)

# Notify the reader that the data was successfully loaded.
data_load_state.text("Loading data...done!")

# Show table
with st.expander("Expand to see data sample"):
    st.markdown("## Example")
    st.dataframe(raw_df.head(3))

# Obtain global variables
num_players = raw_df['Player'].nunique()
num_teams = raw_df['Tm'].nunique()
min_value = math.floor(raw_df.EFF.min())
max_value = math.ceil(raw_df.EFF.max())

# Main variables
column1, column2, _ = st.columns([1,1,3])
column1.metric("Players:", num_players, +10)
column2.metric("Teams:", num_teams, '-1%')

# Sidebar for the filters

st.sidebar.markdown("# Filters")

teams_selected = st.sidebar.multiselect(
     'Select team:',
     raw_df.Tm.unique())

eff_range = st.sidebar.slider('Select range for efficiency:',
                          min_value=min_value,
                          max_value=max_value,
                          value=[min_value,
                                 max_value])

if teams_selected is not None:
    filtered_df = raw_df[raw_df['Tm'].isin(teams_selected)]

if len(eff_range) > 0:
    filtered_df = filtered_df.loc[(filtered_df.EFF > eff_range[0]) &
                    (filtered_df.EFF < eff_range[1]),]

st.markdown("## Team squad")

plt = (
    alt.Chart(filtered_df)
    .mark_circle()
    .encode(
        x=alt.X("TRB:Q", title="Total Rebounds"),
        y=alt.Y("PTS:Q", title="Points per game"),
        color='Tm',
        tooltip=["Player", "EFF"]
    )
    .interactive()
)
plt2 = (
    alt.Chart(filtered_df)
    .mark_circle()
    .encode(
        x=alt.X("MP:Q", title="Minutes per game"),
        y=alt.Y("G:Q", title="Games played"),
        color='Tm',
        tooltip=["Player", "EFF"],
    )
    .interactive()
)

column_1, column_2 = st.columns(2)
with column_1:
    column_1.markdown("**Rebounds vs points**")
    st.altair_chart(plt, use_container_width=True)

with column_2:
    column_2.markdown("**Games vs Minutes**")
    st.altair_chart(plt2, use_container_width=True)