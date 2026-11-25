#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 19:33:35 2026

@author: dina.deifallah
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# Page configuration, title and data source
st.set_page_config(page_title="World Happiness Report", page_icon="🌐", layout='wide')
st.title("🌍 World Happiness Dashboard")
st.caption("Source: World Happiness Report 2023 | Kaggle")

# Data Ingestion
HERE = Path(__file__).parent
# Look for the CSV in ../data (class layout), ./data, or next to this file,
# so the app also works when deployed from a different folder layout.
DATA = next(p for p in [HERE.parent / "data" / "world_happiness_2023.csv",
                        HERE / "data" / "world_happiness_2023.csv",
                        HERE / "world_happiness_2023.csv"] if p.exists())
df = pd.read_csv(DATA)

df.columns = ['Country','Region','Score','GDP','Social_Support',
              'Life_Expectancy','Freedom','Generosity','Corruption']

# Side bar filters
with st.sidebar:
    st.header("Filters")
    regions = ['All Regions'] + sorted(df['Region'].unique().tolist())
    selected_region = st.selectbox("Region", regions)
    top_n = st.slider("Show top N", 5, 25, 15)
    

# filter data by region and top_n
filtered = df if selected_region == 'All Regions' else df[df['Region'] == selected_region]
top = filtered.nlargest(top_n, 'Score').sort_values('Score')

# KPI row 
col1, col2, col3 = st.columns(3)
col1.metric("Countries", len(filtered))
col2.metric("Avg Score", f"{filtered['Score'].mean():.2f}",
            f"{filtered['Score'].mean()-df['Score'].mean():+.2f} vs global")
col3.metric("Happiest", filtered.nlargest(1,'Score')['Country'].values[0])

st.divider()

# create top bar chart
fig = px.bar(top, x='Score', y='Country', orientation='h',
             labels={'Score': 'Happiness Score (0–10)', 'Country': ''},
             template='plotly_white', title=f'Happiest {top_n} Countries in 2023 - {selected_region}')

fig.update_layout(title_font=dict(family='Arial', size=13, color='slategrey'),
                  xaxis=dict(range=[0, 8.0]))


st.plotly_chart(fig, width='stretch', height=600)

st.divider()

# ── CLASS EXERCISE: diverging chart with an annotated midpoint ────────────
# Midpoint = the global average score (all countries, not just the filtered ones).
# Gap > 0 -> happier than the global average, gap < 0 -> less happy.
global_avg = df['Score'].mean()
gap = filtered.assign(Gap=filtered['Score'] - global_avg).sort_values('Gap')

st.subheader("How far is each country from the global average?")

# Two hues (red = below, blue = above) with a neutral grey midpoint at 0.
# The range is symmetric so that grey sits exactly in the middle of the colour bar.
limit = float(df['Score'].sub(global_avg).abs().max())
DIVERGING = [[0.0, '#b2182b'], [0.5, '#d9d9d9'], [1.0, '#2166ac']]

fig2 = px.bar(gap, x='Gap', y='Country', orientation='h',
              color='Gap', color_continuous_scale=DIVERGING,
              color_continuous_midpoint=0, range_color=[-limit, limit],
              labels={'Gap': 'Score minus global average', 'Country': ''},
              hover_data={'Score': ':.2f', 'Gap': ':+.2f'},
              template='plotly_white')

# Annotated midpoint: dashed line at 0 with a label
fig2.add_vline(x=0, line_dash='dash', line_color='slategrey', line_width=1.5,
               annotation_text=f'Midpoint = global average ({global_avg:.2f})',
               annotation_position='top', annotation_font=dict(size=12, color='slategrey'))

fig2.update_layout(height=max(400, 20 * len(gap) + 120),
                   title=dict(text=f'Happiness score vs global average - {selected_region}',
                              font=dict(family='Arial', size=13, color='slategrey')),
                   coloraxis_colorbar=dict(title='Gap', tickvals=[-3, -2, -1, 0, 1, 2, 3],
                                           ticktext=['-3', '-2', '-1', '0', '+1', '+2', '+3']),
                   margin=dict(t=80))
fig2.update_xaxes(zeroline=False)

st.plotly_chart(fig2, width='stretch')

st.divider()
st.caption("Built with Streamlit + Plotly")