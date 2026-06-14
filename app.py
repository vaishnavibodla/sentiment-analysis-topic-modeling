import streamlit as st
import pandas as pd
import sqlite3
from transformers import pipeline

sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

st.set_page_config(
    page_title="Product Review Analytics",
    layout="wide"
)

st.title("🛍️ Product Review Analytics Dashboard")

# Connect to database
conn = sqlite3.connect("database/reviews.db")

# Load data
df = pd.read_sql(
    "SELECT * FROM final_reviews",
    conn
)


# Overview
col1,col2,col3,col4 = st.columns(4)

col1.metric(
    "Total Reviews",
    len(df)
)

col2.metric(
    "Average Rating",
    round(df["Rating"].mean(),2)
)

col3.metric(
    "Positive %",
    round(
        (df["Sentiment"]=="POSITIVE").mean()*100,
        2
    )
)

col4.metric(
    "Recommended %",
    round(
        df["Recommended IND"].mean()*100,
        2
    )
)



st.header("Reviews by Department")

dept = df.groupby(
    "Department Name"
).size()

st.bar_chart(dept)

# Sentiment Distribution
st.header("Sentiment Distribution")

st.bar_chart(
    df["Sentiment"].value_counts()
)

# Topic Distribution
st.header("Topic Distribution")

st.bar_chart(
    df["Topic"].value_counts()
)

sent_rating = pd.crosstab(
    df["Rating"],
    df["Sentiment"]
)

st.header("Rating vs Sentiment")

st.dataframe(sent_rating)



st.header("Review Explorer")

topic_filter = st.selectbox(
    "Select Topic",
    sorted(df["Topic"].unique())
)

sent_filter = st.selectbox(
    "Select Sentiment",
    df["Sentiment"].unique()
)

filtered = df[
    (df["Topic"]==topic_filter)
    &
    (df["Sentiment"]==sent_filter)
]

st.dataframe(
    filtered[
        [
            "Review Text",
            "Rating",
            "Sentiment",
            "Topic"
        ]
    ]
)

#Add Search Box
search_text = st.text_input(
    "Search Review Text"
)

if search_text:
    result = df[
        df["Review Text"]
        .str.contains(
            search_text,
            case=False,
            na=False
        )
    ]

    st.dataframe(result)

from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.header("Word Cloud")

text = " ".join(df["Review Text"].astype(str))

wc = WordCloud(
    width=800,
    height=400,
    background_color="white"
).generate(text)

fig, ax = plt.subplots()

ax.imshow(wc)
ax.axis("off")

st.pyplot(fig)

#Live sentiment prediction
st.header("Predict Review Sentiment")

review = st.text_area(
    "Enter Review"
)

if st.button("Analyze"):

    result = sentiment_pipeline(review)[0]

    st.success(
        f"Sentiment: {result['label']}"
    )

st.header("Export Results")

csv = df.to_csv(index=False)

st.download_button(
    label="Download Analyzed Reviews",
    data=csv,
    file_name="review_analysis.csv",
    mime="text/csv"
)


#To run this again
#run this command in vscode- .\venv\Scripts\Activate.ps1 or venv\Scripts\activate.bat
#then run streamlit run app.py