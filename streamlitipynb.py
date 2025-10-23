try:
    import streamlit as st
except ModuleNotFoundError:
    import os
    os.system("pip install streamlit")
    import streamlit as st

import pandas as pd
import plotly.express as px

# ---- Load data ----
# NOTE: make sure this path is correct in your environment
df = pd.read_csv('Advertising_F.csv')

# ---- App Title ----
st.title("Advertising Effectiveness Dashboard — Clay")

# ---- Sidebar controls ----
st.sidebar.header("Controls")

# If the CSV has exactly these columns, great. If not, we’ll fall back to any that exist.
possible_x = [c for c in ['TV', 'Radio', 'Newspaper'] if c in df.columns]
if not possible_x:
    # fallback: any numeric columns for X
    possible_x = df.select_dtypes('number').columns.tolist()

# y defaults to 'sales' if present, otherwise first numeric column
possible_y = []
if 'sales' in df.columns:
    possible_y = ['sales']
else:
    nums = df.select_dtypes('number').columns.tolist()
    if nums:
        possible_y = [nums[0]]

x_var = st.sidebar.selectbox("X-Axis", possible_x)
y_var = st.sidebar.selectbox("Y-Axis", possible_y)

# ---- Plotly scatter with optional trendline ----
# trendline="ols" needs statsmodels; if not installed, we’ll drop the trendline gracefully
try:
    import statsmodels.api as sm  # noqa: F401
    trend = "ols"
except Exception:
    trend = None

fig = px.scatter(df, x=x_var, y=y_var, trendline=trend, title=f"Scatter: {x_var} vs {y_var}")
st.plotly_chart(fig, use_container_width=True)

# ---- Quick Scatter using Streamlit's native chart (second scatter as requested) ----
st.subheader("Quick Scatter (Streamlit native)")
st.caption("This uses st.scatter_chart for a simple, fast plot.")

# Build a small dataframe with just the chosen x and y
quick_df = df[[x_var, y_var]].dropna()
quick_df = quick_df.rename(columns={x_var: "x", y_var: "y"})
st.scatter_chart(quick_df, x="x", y="y")

# ---- Map section ----
st.title("Store/City Map")
# We expect Latitude / Longitude columns (and optional City, sales, TV).
# Adjust these names to match your CSV exactly.
lat_col = "Latitude"
lon_col = "Longitude"

if lat_col in df.columns and lon_col in df.columns:
    map_fig = px.scatter_mapbox(
        df,
        lat=lat_col,
        lon=lon_col,
        color='sales' if 'sales' in df.columns else None,
        size='TV' if 'TV' in df.columns else None,
        hover_name='City' if 'City' in df.columns else None,
        title="Locations by Sales and TV Spend"
    )
    # Correct style key and value (no token needed for 'carto-positron')
    map_fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=3
    )
    st.plotly_chart(map_fig, use_container_width=True)
else:
    st.warning(
        "Map not shown: columns 'Latitude' and 'Longitude' not found in the CSV. "
        "Please add them or update the column names in the code."
    )
