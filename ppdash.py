import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Load Data
df = pd.read_excel("users_with_location.xlsx")

# Convert Created_At to Date format
df["Created_At"] = pd.to_datetime(df["Created_At"], errors='coerce').dt.date
df = df.dropna(subset=["Created_At"])  # Drop rows where Created_At couldn't be parsed

# Define color mapping for cities
unique_cities = df["City"].unique()
color_map = {city: px.colors.qualitative.Set1[i % len(px.colors.qualitative.Set1)] for i, city in enumerate(unique_cities)}

# Initialize Dash App
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("User Registration Dashboard", style={"textAlign": "center"}),
    
    # Dark mode toggle
    dcc.RadioItems(
        id="theme_selector",
        options=[
            {"label": "Light Mode", "value": "plotly_white"},
            {"label": "Dark Mode", "value": "plotly_dark"}
        ],
        value="plotly_white",
        labelStyle={"display": "inline-block", "margin-right": "10px"}
    ),
    
    # Date Picker
    dcc.DatePickerRange(
        id="date_filter",
        start_date=df["Created_At"].min(),
        end_date=df["Created_At"].max(),
        display_format='YYYY-MM-DD',
    ),
    
    # Dropdown to filter cities
    dcc.Dropdown(
        id="city_filter",
        options=[{"label": city, "value": city} for city in df["City"].unique()],
        multi=True,
        placeholder="Select City (Optional)",
    ),
    
    # Bar Chart with scrollable container
    html.Div([
        dcc.Graph(id="user_trend_graph", style={"width": "100%", "overflowX": "scroll"})
    ]),
    
    # Bigger Pie Chart
    html.Div([
        dcc.Graph(id="user_distribution_pie", style={"height": "600px"})
    ]),
])

# Callback to update the graphs
@app.callback(
    [Output("user_trend_graph", "figure"), Output("user_distribution_pie", "figure")],
    [Input("city_filter", "value"), Input("date_filter", "start_date"), Input("date_filter", "end_date"), Input("theme_selector", "value")]
)
def update_graphs(selected_cities, start_date, end_date, theme):
    # Convert date range to datetime
    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()
    
    # Filter Data by Date Range and City
    filtered_df = df[(df["Created_At"] >= start_date) & (df["Created_At"] <= end_date)]
    if selected_cities:
        filtered_df = filtered_df[filtered_df["City"].isin(selected_cities)]
    
    # Group Data for Bar Chart
    grouped_data = filtered_df.groupby(["Created_At", "City"]).size().reset_index(name="User Count")
    
    # Create Bar Chart with consistent colors
    bar_fig = px.bar(grouped_data,
                      x="Created_At",
                      y="User Count",
                      color="City",
                      title="User Creation Trends by City",
                      labels={"Created_At": "Date", "User Count": "Number of Users", "City": "City"},
                      hover_data={"Created_At": True, "City": True, "User Count": True},
                      barmode="stack",
                      template=theme,
                      color_discrete_map=color_map)
    bar_fig.update_layout(xaxis=dict(type='category'))
    
    # Group Data for Pie Chart
    city_counts = filtered_df["City"].value_counts().reset_index()
    city_counts.columns = ["City", "User Count"]
    
    # Create Pie Chart with consistent colors
    pie_fig = px.pie(city_counts,
                      names="City",
                      values="User Count",
                      title="User Distribution by City",
                      template=theme,
                      hole=0.3,
                      color="City",
                      color_discrete_map=color_map)
    pie_fig.update_traces(textinfo="none", hoverinfo="label+percent+value")
    
    return bar_fig, pie_fig

# Run the Dashboard
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=3000, debug=True)
