import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output, State
import psycopg2
import pandas as pd
import plotly.graph_objs as go
import subprocess

#initialize variables to plot
cash = [10000]
stocks = [0]
time = [0]

#establish initial connection to postgres db to create transactions table
connection = psycopg2.connect(host = 'POSTGRESQL_IP_ADDRESS', database = 'DB_NAME', user = 'DB_USER', password = 'DB_PASSWORD')
cursor = connection.cursor()
cursor.execute('DROP TABLE IF EXISTS transactions;')
cursor.execute('CREATE TABLE IF NOT EXISTS transactions (ticker varchar(255), date varchar(255), time varchar(255), price varchar(255), shares varchar(255));')
cursor.execute('DROP TABLE IF EXISTS portfolio;')
cursor.execute('CREATE TABLE IF NOT EXISTS portfolio (ticker varchar(255), price varchar(255), shares varchar(255));')
#cursor.execute('INSERT INTO portfolio VALUES (CASH, 10000, 0);')
connection.commit()
connection.close()

app = dash.Dash()

app.layout = html.Div(children=[
    html.Div(
    	html.H2('Tradr, a real time trading platform!'),
    	className = 'banner'
    ),
    
    html.Div(children = [
    	html.Button(
    		id = 'startButton',
    		children = 'Start Trading!'
    	),
    
    	html.Button(
    		id = 'stopButton',
    		children = 'Stop Trading!'
    	),
    
    	html.Div(
    		id = 'startLabel'
    	),
    	
    	html.Div(
    		id = 'stopLabel'
    	)
    ]),
    
    html.Div([
        html.Div([
            html.H3("PORTFOLIO VALUE OVER TIME")
        ], className='Title'),
        html.Div([
            dcc.Graph(id='portfolio')
        ]),
        dcc.Interval(id='updateTable', interval=500, n_intervals=0),
    ], className='row wind-speed-row'),
    
    dcc.Graph(
    	id = 'portfolio'
    	),

	dt.DataTable(
			id = 'trades',
			rows=[{}],
        	row_selectable=False,
        	filterable=False,
        	sortable=False,
        	selected_row_indices=[]
		)
])


@app.callback(
	Output('startLabel', 'children'),
	[Input('startButton','n_clicks')]
)
def startTrading(n_clicks):
	if n_clicks > 0:
		subprocess.Popen('bash run.sh', shell=True)
		return 'Started trading!'


@app.callback(
	Output('stopLabel', 'children'),
	[Input('stopButton', 'n_clicks')]
)
def stopTrading(n_clicks):
	if n_clicks > 0:
		subprocess.Popen('bash stop.sh', shell=True)
		return 'Stopped trading.'


@app.callback(
	Output('trades', 'rows'),
	[Input('updateTable','n_intervals')]
)
def updateTable(n):
	connection = psycopg2.connect(host = 'POSTGRESQL_IP_ADDRESS', database = 'DB_NAME', user = 'DB_USER', password = 'DB_PASSWORD')
	data = pd.read_sql_query('SELECT * FROM transactions ORDER BY date DESC, time DESC LIMIT 20;', connection)
	return data.to_dict('records')
	
@app.callback(
	Output('portfolio', 'figure'),
	[Input('trades','rows')]
)
def updateGraph(n_intervals):
	connection = psycopg2.connect(host = 'POSTGRESQL_IP_ADDRESS', database = 'DB_NAME', user = 'DB_USER', password = 'DB_PASSWORD')
	data = pd.read_sql_query('SELECT * FROM portfolio;', connection)
	data = data.to_dict('records')
	sum = 0
	for line in data:
		sum += round(float(line['price'])*float(line['shares']),2)
	stocks.append(sum)
	cash.append(cash[0] - sum)
	
	trace0 = go.Scatter(
		x = time,
		y = stocks,
		mode = 'lines',
		name = 'Stock',
		line = dict(
			color = ('rgb(66, 196, 247)')
		)
	)
	
	layout = dict(
		xaxis = dict(title = 'Elapsed Time (s)'),
		yaxis = dict(title = 'Porfolio Value ($)')
	)
	
	"""
	trace1 = go.Scatter(
		x = time,
		y = stocks,
		mode = 'lines',
		name = 'Stock',
		line = dict(
			color = ('rgb(82, 82, 82)')
		)
	)	
	"""
	
	time.append(time[len(time) - 1] + 1)
		
	return go.Figure(data = [trace0], layout = layout)

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/737dc4ab11f7a1a8d6b5645d26f69133d97062ae/dash-wind-streaming.css",
                "https://fonts.googleapis.com/css?family=Raleway:400,400i,700,700i",
                "https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i"]


for css in external_css:
    app.css.append_css({"external_url": css})

if __name__ == '__main__':
    app.run_server(debug=True, host = '0.0.0.0')
    