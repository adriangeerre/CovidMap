import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly_express as px

st.set_page_config(layout="wide")

st.header("Weekly Cummulative Covid19 map")

# Covid data
@st.cache(allow_output_mutation=True)
def load_input():
	print("Loading data")
	# Load GeoJson
	geoData = gpd.read_file("worldwide.geojson")
	cols = ["name_long","subregion","geometry"]
	geoData = geoData[cols]
	geoData = geoData.rename(columns = {'name_long': 'country'})

	# Load Covid
	file = "https://opendata.ecdc.europa.eu/covid19/nationalcasedeath/csv/data.csv"
	covid = pd.read_csv(file)
	covid = covid.merge(geoData, on = 'country', how='left')

	covid[["population", "weekly_count","cumulative_count"]] = covid[["population", "weekly_count","cumulative_count"]].apply(pd.to_numeric)
	covid = covid[covid["country_code"] != ""]
	covid["ratio100K"] = (covid['cumulative_count']*100000)/covid['population']

	return covid

covid = load_input()


## Sidebar form
st.sidebar.header("Options")
form = st.sidebar.form(key='sidebar_form')

# Select indicator
indic = form.radio("Indicator", ["Cases", "Deaths"])

# Time Range
col1, col2 = form.columns(2)
dates = covid["year_week"].tolist()
start = col1.selectbox("Start Week", dates, index=0) 
end = col2.selectbox("End Week", dates, index=len(dates)-1)

# Select scope
scope = form.selectbox("Area", ["World", "Asia", "Europe", "Africa", "North America", "South America"], index=0)

# Select height and width
height = form.slider("Height", min_value=500, max_value=1500, value=600)
width  = form.slider("Width", min_value=500, max_value=1500, value=900)

# Select animation speed
speed = form.selectbox("Speed", ["SuperFast", "Fast","Default", "Slow", "SuperSlow"], index=2)

speed_opts = {"SuperFast": {'transition_time': 50, 'frame_time': 50},
				"Fast": {'transition_time': 150, 'frame_time': 150},
				"Default": {'transition_time': 300, 'frame_time': 300},
				"Slow": {'transition_time': 500, 'frame_time': 500},
				"SuperSlow": {'transition_time': 800, 'frame_time': 800}}

speed = speed_opts[speed]

# Submit Sidebar
submit_button = form.form_submit_button(label='Submit')


## Plot
st.cache()
def plot_covid(data, indic, scope, height, width, speed):
	data = data[data['indicator'] == indic.lower()]

	if scope == "World":
		fig = px.choropleth(data,
			locations="country_code",
			color="ratio100K",
			hover_name="country",
			color_continuous_scale="magma_r",
			range_color=(0,data["ratio100K"].max()),
			animation_frame="year_week",
			labels={"ratio100K": "{}".format(indic)},
			title="<b>{} per 100k inhabitants</b>".format(indic))
	else:
		fig = px.choropleth(data,
			locations="country_code",
			color="ratio100K",
			hover_name="country",
			color_continuous_scale="magma_r",
			range_color=(0,data["ratio100K"].max()),
			animation_frame="year_week",
			scope=scope.lower(),
			labels={"ratio100K": "{}".format(indic)},
			title="<b>{} per 100k inhabitants in {}</b>".format(indic, scope))

	updatemenus = [{
	'buttons': [
		{'args':
			[None, {'frame': {'duration': speed["frame_time"], 'redraw': True},
			'mode': 'immediate', 'fromcurrent': True,
			'transition': {'duration': speed["transition_time"], 'easing': 'linear'}}],
			'label': '&#9654;',
			'method': 'animate'},
		{'args':
			[[None], {'frame': {'duration': 0, 'redraw': True},
			'mode': 'immediate', 'fromcurrent': True,
			'transition': {'duration': 0, 'easing': 'linear'}}],
			'label': '&#9724;',
			'method': 'animate'}],
	'direction': 'right',
	'pad': {'r': 10, 't': 70},
	'showactive': False,
	'type': 'buttons',
	'x': 0.1,
	'xanchor': 'right',
	'y': 0.2,
	'yanchor': 'top'}]

	sliders = [{
	'currentvalue':
		{"prefix": ""},
	'y': 0.2}]

	fig.update_layout(autosize=False,
		height=height, width=width,
		title_font_size=20,
		sliders=sliders, 
		updatemenus=updatemenus)

	return fig

# Execution
if st.button("Plot {}".format(indic)):
	start_index = dates.index(start)
	end_index = dates.index(end)
	if start_index > end_index:
		st.error('Starting week should be before ending week.')
	else:
		# Filter dates
		dates_list = dates[start_index:end_index+1]
		defined_dates = covid.year_week.isin(dates_list)
		covid = covid[defined_dates]

		# Call plot
		fig = plot_covid(covid, indic, scope, height, width, speed)
		st.write(fig)