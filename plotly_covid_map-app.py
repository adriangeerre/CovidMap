import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly_express as px

st.set_page_config(layout="wide")

st.header("Covid19 animated map")

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
	indic2 = indic.lower()
	data = data[data['indicator'] == indic2]

	if scope == "World":
		fig = px.choropleth(data,
			locations="country_code",
			color="ratio100K",
			hover_name="country",
			color_continuous_scale="magma_r",
			animation_frame="year_week",
			labels={
			"year_week": "Year-Week",
			"ratio100K": "{}".format(indic),
			},
			title="<b>{} per 100k inhabitants</b>".format(indic))
	else:
		scope2 = scope.lower()
		fig = px.choropleth(data,
			locations="country_code",
			color="ratio100K",
			hover_name="country",
			color_continuous_scale="magma_r",
			animation_frame="year_week",
			scope=scope2,
			labels={
			"year_week": "Year-Week",
			"ratio100K": "{}".format(indic),
			},
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
	'y': 0,
	'yanchor': 'top'}]

	sliders = [dict(currentvalue={"prefix": ""})]
	fig.update_layout(autosize=False, height=height, width=width,
		sliders=sliders, title_font_size=20,
		updatemenus=updatemenus)

	return fig

# Call plot
if st.button("Plot {}".format(indic)):
	fig = plot_covid(covid, indic, scope, height, width, speed)
	st.write(fig)
