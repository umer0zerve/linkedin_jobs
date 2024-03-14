import streamlit as st
import plotly.express as px
from wordcloud import WordCloud
import pandas as pd
import matplotlib.pyplot as plt
import requests
from io import StringIO
import gdown

st.set_page_config(layout="wide")

#google_drive_link = 'https://drive.google.com/file/d/1tW9VpAt0R3HdMKE7yiXSKanRjPSJpqkl/view?usp=sharing'
#file_id = google_drive_link.split('/')[-2]
#download_link = f'https://drive.google.com/uc?id={file_id}'
#output_file = 'linkedin_jobs.csv'
#gdown.download(download_link, output_file, quiet=False)

#df = pd.read_csv(output_file)
dfs = [pd.read_csv(os.path.join('./files', filename)) for filename in sorted(os.listdir('./files')) if filename.endswith(".csv")]
df = pd.concat(dfs, ignore_index=True)


linkedin_logo_path = 'linkedin_logo.png'
st.image(linkedin_logo_path, width=150, caption="🔗 LinkedIn Logo")


st.title("🚀 Job Analytics Dashboard 📊")

country_counts = df['search_country'].value_counts().reset_index()
country_counts.columns = ['Country', 'Job Count']
fig1 = px.choropleth(
    country_counts,
    locations='Country',
    locationmode='country names',
    color='Job Count',
    color_continuous_scale='Viridis',
    labels={'Job Count': 'Total Jobs'},
    title='Total Count of Jobs Based on Countries 🌎',
)

fig2 = px.sunburst(df, path=['search_country', 'search_city'], title='Search City in Search Country 🌆')
fig2.update_layout(
    margin=dict(t=0, l=0, r=0, b=0),
    paper_bgcolor='white',
    font=dict(family="Arial", size=12, color="black"),
    sunburstcolorway=["#636efa", "#ef553b", "#00cc96", "#ab63fa", "#19d3f3"],
)

country_job_counts = df.groupby(['search_country', 'job_type']).size().reset_index(name='count')
country_job_counts['percentage'] = country_job_counts.groupby('search_country')['count'].transform(lambda x: x / x.sum() * 100)
fig3 = px.bar(
    country_job_counts, y='search_country', x='percentage',
    color='job_type', title='Job Type Distribution by Country 📈',
    labels={'percentage': 'Percentage of Jobs', 'search_country': 'Country'},
    orientation='h',
    hover_name='job_type',
    category_orders={'search_country': sorted(country_job_counts['search_country'].unique())},
    width=800,
    height=600,
    template='plotly_dark'
)

relevant_columns = ['job_title', 'search_country']
df_subset = df[relevant_columns]
job_counts = df_subset.groupby(['search_country', 'job_title']).size().reset_index(name='job_count')
most_in_demand_jobs = job_counts.groupby('search_country').apply(lambda x: x.nlargest(10, 'job_count')).reset_index(drop=True)
most_in_demand_jobs = most_in_demand_jobs.sort_values(by='job_count', ascending=False)
fig4 = px.bar(
    most_in_demand_jobs, x='job_count', y='job_title', color='search_country',
    labels={'job_count': 'Job Count', 'job_title': 'Job Title'},
    title='Most In-Demand Job Titles by Country 🚀',
    template='plotly_dark',
    height=600, width=800,
    facet_col='search_country',
)
fig4.update_layout(
    xaxis_title='Job Count',
    yaxis_title='Job Title',
    legend_title='Country',
    barmode='stack',
)

relevant_columns = ['job_title', 'job_skills']
df_subset = df[relevant_columns]
df_subset = df_subset.dropna(subset=['job_skills'])
job_counts = df_subset.groupby('job_title').size().reset_index(name='job_count')
top_10_jobs = job_counts.nlargest(10, 'job_count')
top_10_skills_text = ' '.join(df_subset[df_subset['job_title'].isin(top_10_jobs['job_title'])]['job_skills'])
fig5, ax = plt.subplots(figsize=(8, 4))
wordcloud = WordCloud(width=600, height=300, background_color='white').generate(top_10_skills_text)
ax.imshow(wordcloud, interpolation='bilinear')
ax.set_title('Top 10 In-Demand Job Skills')
ax.axis('off')


col1, col2 = st.columns(2)


with col1:
    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig3, use_container_width=True)


with col2:
    st.plotly_chart(fig2, use_container_width=True)
    st.plotly_chart(fig4, use_container_width=True)


st.title("Top 10 In-Demand Job Skills 💼")
st.pyplot(fig5)
