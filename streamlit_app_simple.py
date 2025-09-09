import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="US Population Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    return pd.read_csv('data/us-population-2010-2019-reshaped.csv')

df_reshaped = load_data()

# Sidebar
st.sidebar.title('US Population Dashboard')

year_list = list(df_reshaped.year.unique())[::-1]
selected_year = st.sidebar.selectbox('Select Year', year_list, index=len(year_list)-1)

df_selected_year = df_reshaped[df_reshaped.year == selected_year]
df_selected_year_sorted = df_selected_year.sort_values(by="population", ascending=False)

color_theme_list = ['blues', 'viridis', 'greens', 'reds', 'plasma']
selected_color_theme = st.sidebar.selectbox('Color Theme', color_theme_list, index=0)

# Main title
st.title('US Population Dashboard')

# Helper functions
def format_number(num):
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'

def calculate_population_difference(input_df, input_year):
    selected_year_data = input_df[input_df['year'] == input_year].reset_index()
    previous_year_data = input_df[input_df['year'] == input_year - 1].reset_index()
    selected_year_data['population_difference'] = selected_year_data.population.sub(previous_year_data.population, fill_value=0)
    return pd.concat([selected_year_data.states, selected_year_data.id, selected_year_data.population, selected_year_data.population_difference], axis=1).sort_values(by="population_difference", ascending=False)

# Main content
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader('Population Changes')
    
    if selected_year > 2010:
        df_population_difference_sorted = calculate_population_difference(df_reshaped, selected_year)
        
        # Highest growth
        first_state_name = df_population_difference_sorted.states.iloc[0]
        first_state_population = format_number(df_population_difference_sorted.population.iloc[0])
        first_state_delta = format_number(df_population_difference_sorted.population_difference.iloc[0])
        st.metric(f"Highest Growth: {first_state_name}", first_state_population, first_state_delta)
        
        # Lowest growth
        last_state_name = df_population_difference_sorted.states.iloc[-1]
        last_state_population = format_number(df_population_difference_sorted.population.iloc[-1])
        last_state_delta = format_number(df_population_difference_sorted.population_difference.iloc[-1])
        st.metric(f"Lowest Growth: {last_state_name}", last_state_population, last_state_delta)
    else:
        st.write("No data available for 2010")

with col2:
    st.subheader('Geographic Distribution')
    
    # Choropleth map
    choropleth = px.choropleth(
        df_selected_year, 
        locations='states_code', 
        color='population', 
        locationmode="USA-states",
        color_continuous_scale=selected_color_theme,
        scope="usa",
        labels={'population': 'Population'}
    )
    st.plotly_chart(choropleth, use_container_width=True)

with col3:
    st.subheader('Top States')
    st.dataframe(
        df_selected_year_sorted[['states', 'population']],
        hide_index=True,
        use_container_width=True
    )

# Heatmap
st.subheader('Population Trends (2010-2019)')
heatmap = alt.Chart(df_reshaped).mark_rect().encode(
    y=alt.Y('year:O', title="Year"),
    x=alt.X('states:O', title="States"),
    color=alt.Color('max(population):Q', scale=alt.Scale(scheme=selected_color_theme))
).properties(width=800, height=400)
st.altair_chart(heatmap, use_container_width=True)

# About section
with st.expander('About'):
    st.write('''
    - Data: U.S. Census Bureau
    - Years: 2010-2019
    - Population changes show year-over-year differences
    ''')
