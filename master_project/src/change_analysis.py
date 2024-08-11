import json
import pandas as pd
import plotly.express as px
from pathlib import Path

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def load_combined_data(file_path):
    return pd.read_csv(file_path)

def load_articles(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def calculate_changes(before_data, after_data):
    changes = []

    # Convert before_data to a dictionary for easy lookup
    before_dict = {(entry['user_id'], entry['question']): entry['response'] for entry in before_data}

    for entry in after_data:
        user_id = entry['user_id']
        question = entry['question']
        after_response = entry['response']

        if (user_id, question) not in before_dict:
            continue

        before_response = before_dict[(user_id, question)]

        relevance_change = after_response['relevance'] - before_response['relevance']
        sentiment_change = after_response['sentiment'] - before_response['sentiment']
        agreement_change = (
            (after_response['agreement'] if after_response['agreement'] != "N/A" else 0) - 
            (before_response['agreement'] if before_response['agreement'] != "N/A" else 0)
        )

        change = {
            "user_id": user_id,
            "question": question,
            "relevance_change": relevance_change,
            "sentiment_change": sentiment_change,
            "agreement_change": agreement_change,
            "has_changed": relevance_change != 0 or sentiment_change != 0 or agreement_change != 0,
            "before_response": before_response,
            "after_response": after_response,
            "article_title": entry['article']['title'],
            "article_sentiment": entry['article']['sentiment'],
            "article_url": entry['article']['url']
        }

        changes.append(change)

    return changes

def merge_data(changes, combined_data, articles_data):
    changes_df = pd.DataFrame(changes)
    merged_df = pd.merge(changes_df, combined_data, on="user_id")
    
    # Flatten articles data and merge with changes_df
    article_list = []
    for topic, sentiments in articles_data.items():
        for sentiment, articles in sentiments.items():
            for article in articles:
                article_list.append({
                    "article_title": article["title"],
                    "article_sentiment": article["sentiment"],
                    "article_url": article["url"],
                    "article_body": article["body"][:100],  # truncate body for brevity
                    "article_topic": topic
                })

    articles_df = pd.DataFrame(article_list)
    merged_df = pd.merge(merged_df, articles_df, on=["article_title", "article_sentiment", "article_url"], how="left")
    
    return merged_df

def create_interactive_plot(merged_df):
    # Create an interactive scatter plot
    fig = px.scatter(
        merged_df,
        x="relevance_change",
        y="sentiment_change",
        color="political_orientation",
        size="agreement_change",
        hover_data=["user_id", "question", "article_title", "article_sentiment", "article_topic", "persona_details"],
        title="Opinion Changes After Reading Articles"
    )

    fig.update_layout(
        xaxis_title="Change in Relevance",
        yaxis_title="Change in Sentiment",
        legend_title="Political Orientation"
    )

    fig.show()

def main():
    before_responses = load_json('../data/processed/before_responses.json')
    after_responses = load_json('../data/processed/after_responses.json')
    combined_data = load_combined_data('../data/processed/combined_data.csv')
    articles_data = load_articles('../data/processed/articles.json')

    changes = calculate_changes(before_responses, after_responses)
    merged_df = merge_data(changes, combined_data, articles_data)

    create_interactive_plot(merged_df)

if __name__ == '__main__':
    main()
