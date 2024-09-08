import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_option_menu import option_menu
import requests
import base64

# Setting up page configuration
st.set_page_config(page_title="Airbnb Data Visualization",
                   layout="wide",
                   initial_sidebar_state="expanded")

# Creating option menu in the sidebar
with st.sidebar:
    selected = option_menu("Menu", ["Home", "Overview", "Explore"],
                           icons=["house", "graph-up-arrow", "bar-chart-line"],
                           menu_icon="menu-button-wide",
                           default_index=0,
                           styles={"nav-link": {"font-size": "20px", "text-align": "left", "margin": "-2px", "--hover-color": "#FF5A5F"},
                                   "nav-link-selected": {"background-color": "#FF5A5F"}})
    
# Initializing an empty dataframe in session state
if 'df' not in st.session_state:
    st.session_state['df'] = pd.DataFrame()

# Home Page
if selected == "Home":
    st.markdown("<h1 style='text-align: center; color: #FF5A5F;'>AIRBNB ANALYSIS</h1>", unsafe_allow_html=True)
    
    # Replace with your raw content URL
    image_url = "https://raw.githubusercontent.com/YABASEIMMANUEL/Yab-Analysis-of-AirBNB/main/aribnb.gif"
    
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        image_base64 = base64.b64encode(response.content).decode()
        
        st.markdown(
            f"""
            <style>
            .centered-img {{
                display: block;
                margin-left: auto;
                margin-right: auto;
                width: 50%; /* Adjust width as needed */
            }}
            </style>
            <img src="data:image/gif;base64,{image_base64}" class="centered-img">
            """,
            unsafe_allow_html=True
        )
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching image: {e}")
    
    st.markdown("## :blue[Domain] : Travel Industry, Property Management, and Tourism")
    st.markdown("## :blue[Overview] : In this project, the focus is on analyzing Airbnb data to uncover valuable insights related to pricing, availability, and location trends. Using MongoDB Atlas, the data is meticulously cleaned and prepared to ensure accuracy and consistency. Interactive visualizations and dynamic plots are then developed to provide a clear view of various patterns and trends, such as fluctuations in pricing, seasonal availability, and geographic distribution of properties. This approach aims to deliver actionable insights that can help stakeholders make informed decisions in the travel and property management sectors.")
    st.markdown("## :blue[Technologies used] : The analysis leverages a combination of Python for data manipulation, Pandas for data cleaning and analysis, Plotly for creating interactive and visually appealing charts, Streamlit for developing user-friendly web applications, and MongoDB for efficient data storage and retrieval.")
    st.toast('Created by Yabase Immanuel', icon='🤖')

# Overview Page
if selected == "Overview":
    option = option_menu(
        menu_title="",
        options=['Upload File', 'Data', 'Insights'],
        icons=['arrow-right-circle-fill', 'eye-fill'],
        menu_icon='',
        default_index=0,
        orientation='horizontal'
    )

    if option == "Upload File":
        st.markdown("### Upload Your CSV File")
        uploaded_file = st.file_uploader("Choose a CSV file (up to 500MB)", type="csv")
        
        if uploaded_file is not None:
            if uploaded_file.size > 500 * 1024 * 1024:  # 500MB
                st.error("File size exceeds 500MB. Please upload a smaller file.")
            else:
                if st.button("Submit"):
                    try:
                        # Read the file in chunks
                        chunk_size = 100000  # Adjust as needed
                        chunks = []
                        for chunk in pd.read_csv(uploaded_file, chunksize=chunk_size):
                            chunks.append(chunk)
                        df = pd.concat(chunks, ignore_index=True)
                        st.session_state['df'] = df
                        st.success("File uploaded and processed successfully!")
                    except Exception as e:
                        st.error(f"Error reading file: {e}")

    elif option == "Data":
        if not st.session_state['df'].empty:
            st.markdown("### Data Preview")
            st.write(st.session_state['df'])
        else:
            st.error("No data available. Please upload a CSV file in the Upload File option.")

    elif option == "Insights":
        if not st.session_state['df'].empty:
            df = st.session_state['df']
            st.markdown("### Insights")

            country = st.sidebar.multiselect('Select a country', sorted(df.country.unique()), [])
            prop = st.sidebar.multiselect('Select property_type', sorted(df.property_type.unique()), [])
            room = st.sidebar.multiselect('Select room_type', sorted(df.room_type.unique()), [])
            price = st.slider('Select price', df.price.min(), df.price.max(), (df.price.min(), df.price.max()))

            query = f'country in {country} & room_type in {room} & property_type in {prop} & price >= {price[0]} & price <= {price[1]}'

            col1, col2 = st.columns(2, gap='medium')

            with col1:
                df1 = df.query(query).groupby(["property_type"]).size().reset_index(name="Listings").sort_values(by='Listings', ascending=False)[:10]
                fig = px.bar(df1, title='Top 10 Property Types', x='Listings', y='property_type', orientation='h', color='property_type', color_discrete_sequence=px.colors.sequential.Agsunset, text='Listings')
                fig.update_traces(marker=dict(line=dict(width=0.5, color='black')), textposition='outside', hovertemplate='<b>%{y}</b><br>Listings: %{x}')
                fig.update_layout(title_font_size=20, title_font_family="Arial", xaxis_title='Number of Listings')
                st.plotly_chart(fig, use_container_width=True)

                df2 = df.query(query).groupby(["host_name"]).size().reset_index(name="Listings").sort_values(by='Listings', ascending=False)[:10]
                fig = px.bar(df2, title='Top 10 Hosts with Highest number of Listings', x='Listings', y='host_name', orientation='h', color='host_name', color_discrete_sequence=px.colors.sequential.Agsunset, text='Listings')
                fig.update_traces(marker=dict(line=dict(width=0.5, color='black')), textposition='outside', hovertemplate='<b>%{y}</b><br>Listings: %{x}')
                fig.update_layout(showlegend=False, title_font_size=20, title_font_family="Arial", xaxis_title='Number of Listings')
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                df1 = df.query(query).groupby(["room_type"]).size().reset_index(name="counts")
                fig = px.pie(df1, title='Total Listings in each Room_type', names='room_type', values='counts', color_discrete_sequence=px.colors.sequential.Rainbow)
                fig.update_traces(textposition='outside', textinfo='value+label', pull=[0.1, 0, 0, 0], hovertemplate='<b>%{label}</b><br>Counts: %{value}')
                fig.update_layout(title_font_size=20, title_font_family="Arial")
                st.plotly_chart(fig, use_container_width=True)

                country_df = df.query(query).groupby(['country'], as_index=False)['name'].count().rename(columns={'name': 'Total_Listings'})
                fig = px.choropleth(country_df, title='Total Listings in each Country', locations='country', locationmode='country names', color='Total_Listings', hover_name='country', hover_data={'Total_Listings': True}, color_continuous_scale=px.colors.sequential.Plasma)
                fig.update_layout(title_font_size=20, title_font_family="Arial")
                st.plotly_chart(fig, use_container_width=True)

        else:
            st.error("No data available. Please upload a CSV file in the Upload File option.")

# Explore Page
if selected == "Explore" and not st.session_state['df'].empty:
    st.toast('Created by Yabase Immanuel', icon='🤖')
    df = st.session_state['df']
    st.markdown("## Explore more about the Airbnb data")

    country = st.sidebar.multiselect('Select a country', sorted(df.country.unique()), [])
    prop = st.sidebar.multiselect('Select property_type', sorted(df.property_type.unique()), [])
    room = st.sidebar.multiselect('Select room_type', sorted(df.room_type.unique()), [])
    price = st.slider('Select price', df.price.min(), df.price.max(), (df.price.min(), df.price.max()))

    query = f'country in {country} & room_type in {room} & property_type in {prop} & price >= {price[0]} & price <= {price[1]}'

    st.markdown("## Price Analysis")

    col1, col2 = st.columns(2, gap='medium')

    with col1:
        pr_df = df.query(query).groupby('room_type', as_index=False)['price'].mean().sort_values(by='price')
        fig = px.bar(data_frame=pr_df, x='room_type', y='price', color='price', title='Avg Price in each Room Type', color_continuous_scale=px.colors.sequential.Agsunset, text='price')
        fig.update_traces(textposition='outside', hovertemplate='<b>%{x}</b><br>Avg price: %{y}')
        fig.update_layout(title_font_size=20, title_font_family="Arial", xaxis_title='Room Type', yaxis_title='Avg Price')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("## Availability Analysis")

        pra_df = df.query(query).groupby('property_type', as_index=False)['availability_365'].mean().sort_values(by='availability_365')
        fig = px.bar(data_frame=pra_df, x='property_type', y='availability_365', color='availability_365', title='Avg Availability by Property Type', color_continuous_scale=px.colors.sequential.Rainbow, text='availability_365')
        fig.update_traces(textposition='outside', hovertemplate='<b>%{x}</b><br>Avg Availability: %{y}')
        fig.update_layout(title_font_size=20, title_font_family="Arial", xaxis_title='Property Type', yaxis_title='Avg Availability')
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("## Reviews Analysis")
        pr_df = df.query(query).groupby('property_type', as_index=False)['number_of_reviews'].count().sort_values(by='number_of_reviews')
        fig = px.bar(data_frame=pr_df, x='property_type', y='number_of_reviews', color='number_of_reviews', title='Number of Reviews by Property Type', color_continuous_scale=px.colors.sequential.Agsunset, text='number_of_reviews')
        fig.update_traces(textposition='outside', hovertemplate='<b>%{x}</b><br>Number of Reviews: %{y}')
        fig.update_layout(title_font_size=20, title_font_family="Arial", xaxis_title='Property Type', yaxis_title='Number of Reviews')
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        country_df = df.query(query).groupby('country', as_index=False)['price'].mean()
        fig = px.scatter_geo(data_frame=country_df, locations='country', color='price', hover_data=['price'], locationmode='country names', size='price', title='Avg Price in each Country', color_continuous_scale='agsunset')
        fig.update_traces(marker=dict(line=dict(width=0.5, color='black')), hovertemplate='<b>%{location}</b><br>Avg price: %{marker.size}')
        fig.update_layout(title_font_size=20, title_font_family="Arial")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#   ")

        country_df = df.query(query).groupby('country', as_index=False)['availability_365'].mean()
        country_df['availability_365'] = country_df['availability_365'].astype(int)
        fig = px.scatter_geo(data_frame=country_df, locations='country', color='availability_365', hover_data=['availability_365'], locationmode='country names', size='availability_365', title='Avg Availability in each Country', color_continuous_scale='agsunset')
        fig.update_traces(marker=dict(line=dict(width=0.5, color='black')), hovertemplate='<b>%{location}</b><br>Avg Availability: %{marker.size}')
        fig.update_layout(title_font_size=20, title_font_family="Arial")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#   ")

        def categorize_rating(rating):
            if rating < 60:
                return 'Star Rate 1'
            elif 60 <= rating < 70:
                return 'Star Rate 2'
            elif 70 <= rating < 80:
                return 'Star Rate 3'
            elif 80 <= rating < 90:
                return 'Star Rate 4'
            else:
                return 'Star Rate 5'

        df['star_rate_category'] = df['rating'].apply(categorize_rating)
        grouped_df = df.query(query).groupby('rating')['star_rate_category'].count().reset_index()

        fig = px.bar(grouped_df, x='rating', y='star_rate_category', title='Number of Reviews by Rating Category')
        fig.update_layout(xaxis_title='Rating', yaxis_title='Number of Reviews')
        st.plotly_chart(fig, use_container_width=True)
