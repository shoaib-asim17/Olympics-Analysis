import numpy as np
import pandas as pd

def fetch_medal_tally(df, year, country):
    medal_df = df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    flag = 0

    if year == 'Overall' and country == 'Overall':
        temp_df = medal_df
    elif year == 'Overall' and country != 'Overall':
        flag = 1
        temp_df = medal_df[medal_df['region'] == country]
    elif year != 'Overall' and country == 'Overall':
        temp_df = medal_df[medal_df['Year'] == int(year)]
    else:
        temp_df = medal_df[(medal_df['Year'] == int(year)) & (medal_df['region'] == country)]

    if flag == 1:
        x = temp_df.groupby('Year').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Year').reset_index()
    else:
        x = temp_df.groupby('region').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Gold', ascending=False).reset_index()

    x['total'] = x['Gold'] + x['Silver'] + x['Bronze']
    return x

def medal_tally(df):
    medal_df = df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    medal_df = medal_df.groupby('region').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Gold', ascending=False).reset_index()
    medal_df['total'] = medal_df['Gold'] + medal_df['Silver'] + medal_df['Bronze']
    return medal_df

def country_year_list(df):
    years = df['Year'].unique().tolist()
    years.sort()
    years.insert(0, 'Overall')

    countries = np.unique(df['region'].dropna().values).tolist()
    countries.sort()
    countries.insert(0, 'Overall')

    return years, countries

def data_over_time(df, column):
    data_over_time = (
        df.drop_duplicates(['Year', column])
          .groupby('Year')
          .size()
          .reset_index(name='No of Countries')
    )
    data_over_time = data_over_time.rename(columns={'Year': 'Edition'})
    return data_over_time


# def most_successful(df,sport):
#     temp_df = df.dropna(subset=['Medal'])
#     if sport != 'Overall':
#         temp_df = temp_df[temp_df['Sport'] == sport]
#
#     x=temp_df['Name'].value_counts().reset_index().head(15).merge(df,left_on='index',right_on='Name',how='left')[
#         ['index','Name_x','Sport','region']
#     ].drop_duplicates('index')
#     x.rename(columns={'index':'Name','Name_x':'Medal'},inplace=True)
#     return x

def most_successful(df, sport):
    # Filter only medal-winning rows
    temp_df = df.dropna(subset=['Medal'])

    # Filter by sport if not overall
    if sport != 'Overall':
        temp_df = temp_df[temp_df['Sport'] == sport]

    # Count medals per athlete
    top_athletes = temp_df['Name'].value_counts().reset_index().head(15)
    top_athletes.columns = ['Name', 'Medal']

    # Merge to get sport and region info
    merged_df = top_athletes.merge(temp_df[['Name', 'Sport', 'region']], on='Name', how='left')

    # Drop duplicates to avoid repeating athletes
    merged_df = merged_df.drop_duplicates('Name')

    return merged_df


# def yearwise_medal_tally(df,country):
#     temp_df = df.dropna(subset=['Medal'])
#     temp_df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'], inplace=True)
#     new_df = temp_df[temp_df['region'] == country]
#     final_df = new_df.groupby('Year').count()['Medal'].reset_index()
#
#     return final_df

def yearwise_medal_tally(df, country):
    # Keep only medal-winning rows
    temp_df = df.dropna(subset=['Medal'])

    # Drop duplicate medal entries (only unique medals)
    temp_df = temp_df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])

    # Filter by country
    country_df = temp_df[temp_df['region'] == country]

    # Group by year and count medals
    final_df = country_df.groupby('Year').size().reset_index(name='Medal')

    return final_df


def country_event_heatmap(df, country):
    # Drop rows without medals
    temp_df = df.dropna(subset=['Medal'])

    # Drop duplicate medal events
    temp_df = temp_df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])

    # Filter by country
    country_df = temp_df[temp_df['region'] == country]

    # Create a pivot table: Sport vs Year
    heatmap_df = country_df.pivot_table(index='Sport', columns='Year', values='Medal', aggfunc='count').fillna(0)

    return heatmap_df


# def most_successful_countrywise(df, sport):
#     # Filter only medal-winning rows
#     temp_df = df.dropna(subset=['Medal'])
#     temp_df = temp_df[temp_df['region']==country]
#     x=temp_df['Name'].value_counts().reset_index().head(15).merge(df,left_on='index',
#                                                                   right_on='Name',how='left')[
#         ['index']
#     ]
#
#
#
#     return x

def most_successful_countrywise(df, country, sport='Overall'):
    # Filter only medal-winning rows
    temp_df = df.dropna(subset=['Medal'])

    # Filter by country
    temp_df = temp_df[temp_df['region'] == country]

    # Optional: Filter by sport
    if sport != 'Overall':
        temp_df = temp_df[temp_df['Sport'] == sport]

    # Count medals by athlete
    top_athletes = temp_df['Name'].value_counts().reset_index().head(10)
    top_athletes.columns = ['Name', 'Medal']

    # Merge to get additional info (sport, region)
    merged_df = top_athletes.merge(temp_df[['Name', 'Sport', 'region']], on='Name', how='left')

    # Drop duplicate names (since some athletes have multiple entries)
    final_df = merged_df.drop_duplicates('Name')

    return final_df

def weight_v_height(df,sport):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])
    athlete_df['Medal'].fillna('No Medal', inplace=True)
    if sport != 'Overall':
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        return temp_df
    else:
        return athlete_df

def men_vs_women(df):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    men = athlete_df[athlete_df['Sex'] == 'M'].groupby('Year').count()['Name'].reset_index()
    women = athlete_df[athlete_df['Sex'] == 'F'].groupby('Year').count()['Name'].reset_index()

    final = men.merge(women, on='Year', how='left')
    final.rename(columns={'Name_x': 'Male', 'Name_y': 'Female'}, inplace=True)

    final.fillna(0, inplace=True)

    return final