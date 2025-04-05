import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Load Data
df = pd.read_excel("users_with_location.xlsx")

# Convert Created_At to Date format
df["Created_At"] = pd.to_datetime(df["Created_At"], errors='coerce').dt.date

# Initialize Dash App
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("User Registration Dashboard", style={"textAlign": "center"}),

    # Dropdown to filter cities
    dcc.Dropdown(
        id="city_filter",
        options=[{"label": city, "value": city} for city in df["City"].unique()],
        multi=True,
        placeholder="Select City (Optional)",
    ),

    # Graph
    dcc.Graph(id="user_trend_graph"),

])

# Callback to update the graph
@app.callback(
    Output("user_trend_graph", "figure"),
    [Input("city_filter", "value")]
)
def update_graph(selected_cities):
    # Filter Data
    filtered_df = df if not selected_cities else df[df["City"].isin(selected_cities)]

    # Group Data
    grouped_data = filtered_df.groupby(["Created_At", "City"]).size().reset_index(name="User Count")

    # Create Plotly Figure
    fig = px.bar(grouped_data,
                 x="Created_At",
                 y="User Count",
                 color="City",
                 title="User Creation Trends by City",
                 labels={"Created_At": "Date", "User Count": "Number of Users", "City": "City"},
                 hover_data={"Created_At": True, "City": True, "User Count": True})

    # Update Layout
    fig.update_layout(
        xaxis=dict(title="Date", tickangle=-45),
        yaxis_title="Number of Users",
        legend_title="City",
        barmode="stack",
        template="plotly_white"  # Clean white theme
    )

    return fig

# Run the Dashboard
if __name__ == "__main__":
    app.run(debug=True)
