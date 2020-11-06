import pandas as pd
import streamlit as st
import plotly.express as px

st.title("Top 20 doctorate-granting institutions ranked by number of minority U.S. citizen" +
         "and permanent resident doctorate recipients, by ethnicity and race of recipient")

@st.cache
def load_data():
    data = pd.read_csv("https://raw.githubusercontent.com/oena/oena.github.io/master/assets/tsv/cleaned_US_phds_awarded_by_year.tsv",
                       sep="\t")
    return data

data_load_state = st.text("Loading data...")
data = load_data()
data_load_state.text("") # Remove "loading data" after it's loaded

# checkbox to provide option of looking at raw data
if st.sidebar.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

# Add slider to filter line plot data by decade
decade_to_filter = st.sidebar.slider("Year", 1958, 2000, 2017)
filtered_data = data[data["Year"] <= decade_to_filter]

# Make a simple interactive line plot of PhDs awarded, colored by decade
fig1 = px.line(filtered_data,
              x="Year",
              y="Doctorate recipients",
              hover_data=["Year",
                          "Doctorate recipients",
                          "% change from previous year"],
              title="Number of PhD recipients in the US by year")
st.plotly_chart(fig1)

fig2 = px.box(filtered_data,
               x="decade",
               y="% change from previous year",
               color="decade",
               title="Percent change in PhDs awarded, by decade")
st.plotly_chart(fig2)

