import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly_express as px

st.set_page_config(layout="wide")

st.header("Covid19 world map")

# GeoJson
geoData = gpd.read_file("worldwide.geojson")
cols = ["name_long","subregion","geometry"]
geoData = geoData[cols]
geoData = geoData.rename(columns = {'name_long': 'country'})

# Covid data
file = "https://opendata.ecdc.europa.eu/covid19/nationalcasedeath/csv/data.csv"
covid = gpd.read_file("covid_worlwide_weekly.csv")
covid = covid.drop(columns=['geometry'])
covid = covid.merge(geoData, on = 'country', how='left')

covid[["population", "weekly_count","cumulative_count"]] = covid[["population", "weekly_count","cumulative_count"]].apply(pd.to_numeric)
covid = covid[covid["country_code"] != ""]
covid["ratio100K"] = (covid['cumulative_count']*100000)/covid['population']

# Select indicator
indic = st.sidebar.radio("Indicator", ["Cases", "Deaths"])

# Select scope
scope = st.sidebar.radio("Area", ["Worldwide", "Asia", "Europe", "Africa"])

# Select height and width
height = st.sidebar.slider("Height", min_value=500, max_value=1500)
width  = st.sidebar.slider("Width", min_value=800, max_value=2300)

# Select animation speed
transition_time = st.sidebar.slider("Transition time", min_value=10, max_value=100)
frame_time = st.sidebar.slider("Frame time", min_value=5, max_value=100)

# Plot
def plot_covid(data, indic, scope, height, widht, transition_time, frame_time):
	indic = indic.lower()
	data = data[data['indicator'] == indic]

	if scope == "Worldwide":
		fig = px.choropleth(data,
			locations="country_code",
			color="ratio100K",
			hover_name="country",
			color_continuous_scale="magma_r",
			animation_frame="year_week")
	else:
		scope = scope.lower()
		fig = px.choropleth(data,
			locations="country_code",
			color="ratio100K",
			hover_name="country",
			color_continuous_scale="magma_r",
			animation_frame="year_week",
			scope=scope)

	fig.update_layout(autosize=False, height=height, width=width)
	#fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = frame_time
	#fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = transition_time

	st.write(fig)

# Call plot
if st.button("Plot {}".format(indic)):
	plot_covid(covid, indic, scope, height, width, transition_time, frame_time)