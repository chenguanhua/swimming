import streamlit as st
import pandas as pd
from pathlib import Path
import numpy as np
import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.express as px

st.title("Data")
st.markdown("The result is shown below: ")
st.sidebar.title("Options")

# read data and find medalists
path = Path(__file__).parent / 'Olympic_Swimming_Results_1912to2020.csv'

df = pd.read_csv(path)
df = df.rename(columns={'Distance (in meters)' : 'Distance'})

na = df[df.isna().any(axis=1)]
df.dropna(inplace=True)

rank0 = df[df['Rank'] == '0']
df.drop(rank0.index, inplace=True)

rank4 = df[df['Rank'] == '4']
df.drop(rank4.index, inplace=True)

df = df[~df['Results'].isin(['Did not start', 'Did not finish', 'Disqualified'])]
df = df[~df['Results'].str.contains('est')]

def process_time(x):
    ret = float(x[-1])
    if len(x) >= 2:
        ret += float(x[-2]) * 60
    if len(x) == 3:
        ret += float(x[-3]) * 3600
    return ret

df['time'] = df['Results'].str.split(':').apply(process_time)

chart = st.sidebar.selectbox(
    'Which visualization would you like to see?',
    ['None', 'Sunburst', 'Line', 'Bubble'])

if chart == 'None':
    st.dataframe(df)
# Sunburst
elif chart == 'Sunburst':

    cnt = st.sidebar.selectbox(
        'Count?',
        range(2, 5))

    athletes = df.groupby(['Athlete', 'Gender', 'Team', 'Distance', 'Stroke']).size().reset_index(name='Count')

    athletics = athletes[athletes['Count'] >= cnt].sort_values(['Distance', 'Stroke'])

    fig = px.sunburst(athletics, path=['Distance', 'Stroke', 'Athlete'], values='Count', hover_data=['Team', 'Gender'])

    fig.update_layout(title=f'Athletes with {cnt} or more medals in a category', height=600)

    st.plotly_chart(fig)

# Lineplot
elif chart == 'Line':
    cat = st.sidebar.selectbox(
        'Category?',
        df['Distance'].unique())

    stroke = st.sidebar.selectbox(
        'Stroke?',
        df['Stroke'].unique())

    athletes = df[(df['Distance']==cat)&(df['Stroke']==stroke)&(df['Rank']==1)]

    fig = px.line(athletes, x='Year', y='time', color='Gender')
    st.plotly_chart(fig)

# Bubble chart
elif chart == 'Bubble':
    athletes = df.groupby(['Year', 'Team', 'Stroke', 'Rank']).size().reset_index(name='Count')

    fig = px.scatter(athletes, x="Year", y="Rank",
                     size="Count", color="Stroke", size_max=60)
    st.plotly_chart(fig)