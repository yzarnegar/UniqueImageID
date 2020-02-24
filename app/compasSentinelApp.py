import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.graph_objects as go
import pandas as pd
import geopandas as gpd
import pandas as pd
from geopandas import GeoDataFrame
from shapely.geometry import Point, Polygon
import shapely

def query_data(bbox, gdf):
    """
    The function to query a geodataframe based on a bounding box.
    Parameters:
        bbox: a list of coordinates as [south, north, west, east]
        gdf: the geopandas dataframe whose geometry is polygon

    Returns:
        query_result: a data frame of all bursts whose boundary interset with input bbox
        query: index of the rows of geopandas dataframe whose burst's boundaries interset with input bbox 
    """

    s,n,w,e = bbox
    poly = Polygon(zip([w,e,e,w], [s,s,n,n]))
    x,y = poly.exterior.xy
    query = gdf.intersects(poly)
    bb = gdf[query].burst_ID.to_list()
    query_result = sdata[sdata.burst_ID.isin(bb)]
    query_result = query_result.sort_values(by=["burst_ID"])
    return query_result, query


def plot_gpd(fig, gp_df, color='blue'):
    """
    plots the geopandas data frame
    """
    for ii in range(gp_df.shape[0]):
        p1=gp_df.geometry.iloc[ii]
        x,y=p1.exterior.xy
        fig.add_trace(
        go.Scattergeo(
        lat = y.tolist(),
        lon = x.tolist(),
        mode = 'lines',
        line = dict(width = 2, color = color),
))

def plot_poly(fig, x,y, color='blue'):
    """
    plots a polygon
    """

    fig.add_trace(
    go.Scattergeo(
    lat = y,
    lon = x, 
    mode = 'lines',
    line = dict(width = 2, color = color),
))



FILE_NAME = "burstID_database-2.csv"
FILE_NAME2= "burstID_database_tseries.csv"
df = pd.read_csv(FILE_NAME, delimiter=",")
gdf = GeoDataFrame(crs={'init': 'epsg:4326'},
                    geometry=[shapely.wkt.loads(x) for x in df.geometry])

sdata=pd.read_csv(FILE_NAME2,delimiter =",")
gdf["burst_ID"] = df.burst_ID.to_list()
gdf["latitude"] = df.latitude.to_list()
gdf["longitude"] = df.longitude.to_list()
gdf["pass_direction"] = df.pass_direction.to_list()


result, queryIdx = query_data([34,34.5,-120,-119], gdf)
cols = [{"name": i, "id": i} for i in result.columns]
result = result.to_dict('records')


app = dash.Dash(__name__)
app.layout = html.Div([
     html.H4(children='CompasSentinel'),
     html.Button('Search', id="button"),
        dcc.Input(id='south',value=34,  type='number', placeholder="south"),
        dcc.Input(id='north', value=34.5, type='number', placeholder="north"),
        dcc.Input(id='west', value=-120, type='number', placeholder="west"),
        dcc.Input(id='east', value=-119, type='number', placeholder="east"),
        dcc.Graph(id='graph'),
        html.Div(id='my-div'),
        dash_table.DataTable(
            id='table',
                columns=cols, 
                    data=result 
                    )])

@app.callback(
    [dash.dependencies.Output('graph', 'figure'), 
        dash.dependencies.Output('table', 'data')],
    [dash.dependencies.Input('button', 'n_clicks')],
    [dash.dependencies.State("south","value"),
             dash.dependencies.State("north","value"),
             dash.dependencies.State("west","value"),
             dash.dependencies.State("east","value")])
def update_output_div(n_clicks,south, north, west, east):
    box = [south,north,west,east]
    result, query_idx = query_data(box, gdf)
    x = [west, east,east,west, west]
    y = [south, south, north, north, south]
    
    fig = go.Figure()
    plot_gpd(fig,gdf)
    plot_gpd(fig,gdf[query_idx], color='orange')
    plot_poly(fig, x, y, color='red')

    fig.update_layout(
      showlegend = False, geo_scope='usa')

    return fig, result.to_dict('records')


if __name__ == '__main__':
        app.run_server(debug=True)

