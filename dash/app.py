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
connection.commit()
connection.close()

app = dash.Dash()

#div containing html and dash elements that are displayed on the page
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

#function that initiates producer script and spark submit upon button click
#see run.sh for information on how to start producer and submit spark job
@app.callback(
	Output('startLabel', 'children'),
	[Input('startButton','n_clicks')]
)
def startTrading(n_clicks):
	if n_clicks > 0:
		subprocess.Popen('bash run.sh', shell=True)
		return 'Started trading!'

#function that stops producer script and spark job upon button click
#see stop.sh for information on how to stop producer and spark submit job
@app.callback(
	Output('stopLabel', 'children'),
	[Input('stopButton', 'n_clicks')]
)
def stopTrading(n_clicks):
	if n_clicks > 0:
		subprocess.Popen('bash stop.sh', shell=True)
		return 'Stopped trading.'

#displays the 20 most recent trades - updates every 0.5s
@app.callback(
	Output('trades', 'rows'),
	[Input('updateTable','n_intervals')]
)
def updateTable(n):
	connection = psycopg2.connect(host = 'POSTGRESQL_IP_ADDRESS', database = 'DB_NAME', user = 'DB_USER', password = 'DB_PASSWORD')
	data = pd.read_sql_query('SELECT * FROM transactions ORDER BY date DESC, time DESC LIMIT 20;', connection)
	return data.to_dict('records')

#displays the current value of the portfolio every 0.5s
@app.callback(
	Output('portfolio', 'figure'),
	[Input('trades','rows')]
)
def updateGraph(n_intervals):
	connection = psycopg2.connect(host = 'POSTGRESQL_IP_ADDRESS', database = 'DB_NAME', user = 'DB_USER', password = 'DB_PASSWORD')
	data = pd.read_sql_query('SELECT * FROM portfolio;', connection)
	data = data.to_dict('records')
	sum = 0
	#sum the value of each stock owned to find total value of portfolio
	for line in data:
		sum += round(float(line['price'])*float(line['shares']),2)
		
	#maintain time series of stock value and cash value
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
	
	#keep track of elapsed seconds
	time.append(time[len(time) - 1] + 1)
		
	return go.Figure(data = [trace0], layout = layout)

#css sheets used to style graphs, headers, etc.
external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/737dc4ab11f7a1a8d6b5645d26f69133d97062ae/dash-wind-streaming.css",
                "https://fonts.googleapis.com/css?family=Raleway:400,400i,700,700i",
                "https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i"]

for css in external_css:
    app.css.append_css({"external_url": css})

if __name__ == '__main__':
    app.run_server(debug=True, host = '0.0.0.0')
    
