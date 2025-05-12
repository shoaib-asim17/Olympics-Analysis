import streamlit as st
import pandas as pd
import plotly.express as px
import preprocessor, helper
from helper import medal_tally
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff

# Load data
df = pd.read_csv("athlete_events.csv")
region_df = pd.read_csv("noc_regions.csv")

st.sidebar.header("Olympics Analysis")

# Preprocess the data
df = preprocessor.preprocess(df, region_df)

# Sidebar menu
user_menu = st.sidebar.radio(
    'Select an option',
    ('Medal Tally', 'Overall Analysis', 'Country-wise Analysis', 'Athlete-wise Analysis')
)

# Medal Tally section
if user_menu == 'Medal Tally':
    st.sidebar.header("Medal Tally")
    years, countries = helper.country_year_list(df)

    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", countries)

    medal_df = helper.fetch_medal_tally(df, selected_year, selected_country)

    title = f"Medal Tally for {selected_country} in {selected_year}" if selected_year != 'Overall' and selected_country != 'Overall' \
        else f"{selected_country} - {selected_year} Medal Tally"
    st.title(title)
    st.table(medal_df)

# Overall Analysis section
if user_menu == 'Overall Analysis':
    editions = df['Year'].nunique() - 1
    cities = df['City'].nunique()
    sports = df['Sport'].nunique()
    events = df['Event'].nunique()
    athletes = df['Name'].nunique()
    nations = df['region'].nunique()

    st.title("Top Statistics")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Editions")
        st.header(editions)
    with col2:
        st.subheader("Hosts")
        st.header(cities)
    with col3:
        st.subheader("Sports")
        st.header(sports)

    col4, col5, col6 = st.columns(3)
    with col4:
        st.subheader("Events")
        st.header(events)
    with col5:
        st.subheader("Nations")
        st.header(nations)
    with col6:
        st.subheader("Athletes")
        st.header(athletes)

    # Participating Nations Over Time
    nations_over_time = helper.data_over_time(df, 'region')
    fig = px.line(
        nations_over_time,
        x="Edition",
        y="No of Countries",
        title="Participating Nations Over Time"
    )
    st.plotly_chart(fig)

    # Events Over Time
    events_over_time = helper.data_over_time(df, 'Event')
    fig = px.line(
        events_over_time,
        x="Edition",
        y="No of Countries",
        title="Events Over Time"
    )
    st.plotly_chart(fig)

    # Athletes Over Time
    athletes_over_time = helper.data_over_time(df, 'Name')
    fig = px.line(
        athletes_over_time,
        x="Edition",
        y="No of Countries",
        title="Athletes Over Time"
    )
    st.plotly_chart(fig)

    st.title("No of Events over time(Every Sport)")
    fig,ax = plt.subplots(figsize=(20,20))
    x = df.drop_duplicates(['Year','Sport','Event'])
    sns.heatmap(x.pivot_table(index='Sport', columns='Year', values='Event',aggfunc='count').fillna(0).astype('int'),annot=True)
    st.pyplot(fig)

    st.title("Most Successful Athletes")

    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0,'Overall')

    selected_sport = st.selectbox('Select a Sport',sport_list)
    x=helper.most_successful(df,selected_sport)
    st.table(x)


if user_menu == 'Country-wise Analysis':
    st.sidebar.title('Counrty-wise Analysis')

    country_list = df['region'].dropna().unique().tolist()
    country_list.sort()

    selected_country = st.sidebar.selectbox('Select a country',country_list)

    country_df = helper.yearwise_medal_tally(df,selected_country)
    fig = px.line(country_df,x="Year", y="Medal")
    st.title(selected_country + " Medal Tally over the years")
    st.plotly_chart(fig)

    st.title(selected_country + " Excels in the following Sports")

    pt = helper.country_event_heatmap(df,selected_country)
    fig,ax = plt.subplots(figsize=(20,20))
    ax = sns.heatmap(pt,annot=True)
    st.pyplot(fig)

    st.title("Top 10 Athletes of "+selected_country)
    top10_df = helper.most_successful_countrywise(df,selected_country)
    st.table(top10_df)




if user_menu == 'Athlete-wise Analysis':
    # Age distribution for all athletes (deduplicated by name & region to avoid multiple entries per athlete)
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])
    x1 = athlete_df['Age'].dropna()

    # Age distribution for medalists (from full dataset to include all medals)
    x2 = df[df['Medal'] == 'Gold']['Age'].dropna()
    x3 = df[df['Medal'] == 'Silver']['Age'].dropna()
    x4 = df[df['Medal'] == 'Bronze']['Age'].dropna()

    # Create distribution plot
    fig = ff.create_distplot([x1, x2, x3, x4],
                             ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'],
                             show_hist=False, show_rug=False)

    st.title("Distribution of Age")

    st.plotly_chart(fig)

    # Distribution of Age with respect to Sports (Gold Medalists)
    x = []
    name = []

    famous_sports = [
        'Basketball', 'Judo', 'Football', 'Tug-Of-War', 'Athletics', 'Swimming',
        'Badminton', 'Sailing', 'Gymnastics', 'Art Competitions', 'Handball',
        'Weightlifting', 'Wrestling', 'Water Polo', 'Hockey', 'Rowing', 'Fencing',
        'Shooting', 'Boxing', 'Taekwondo', 'Cycling', 'Diving', 'Canoeing',
        'Tennis', 'Golf', 'Softball', 'Archery', 'Volleyball',
        'Synchronized Swimming', 'Table Tennis', 'Baseball',
        'Rhythmic Gymnastics', 'Rugby Sevens', 'Beach Volleyball', 'Triathlon',
        'Rugby', 'Polo', 'Ice Hockey'
    ]

    for sport in famous_sports:
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        x.append(temp_df[temp_df['Medal'] == 'Gold']['Age'].dropna())
        name.append(sport)

    fig = ff.create_distplot(x, name, show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=1000, height=600)

    st.title("Distribution of Age wrt Sports (Gold Medalists)")
    st.plotly_chart(fig)

    # Height vs Weight Analysis
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')

    st.title('Height vs Weight')
    selected_sport = st.selectbox('Select a Sport', sport_list)
    temp_df = helper.weight_v_height(df, selected_sport)

    fig, ax = plt.subplots()
    sns.scatterplot(
        x=temp_df['Weight'],
        y=temp_df['Height'],
        hue=temp_df['Medal'],
        style=temp_df['Sex'],
        s=60,
        ax=ax
    )
    st.pyplot(fig)

    # Men vs Women Participation Over the Years
    st.title("Men vs Women Participation Over the Years")
    final = helper.men_vs_women(df)
    fig = px.line(final, x="Year", y=["Male", "Female"])
    fig.update_layout(autosize=False, width=1000, height=600)
    st.plotly_chart(fig)