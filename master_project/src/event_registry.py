import json
import time
import logging
from eventregistry import EventRegistry, QueryArticlesIter, QueryItems
from pathlib import Path

API_KEY = "ed73bf40-38fd-4de9-8534-f079b53d2eb4"  # Replace with your actual API key
CACHE_FILE = "article_cache.json"
MAX_RETRIES = 3
RETRY_WAIT_TIME = 3600  # 1 hour

class News:
    def __init__(self, config_path="../data/raw/topics.json"):
        self.er = EventRegistry(API_KEY)
        self.topics_path = config_path
        self.cache = self.load_cache()
        with open(self.topics_path, "r") as f:
            self.topic_parameters = json.load(f)
            self.available_topics = list(self.topic_parameters.keys())

    def load_cache(self):
        if Path(CACHE_FILE).exists():
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_cache(self):
        with open(CACHE_FILE, "w") as f:
            json.dump(self.cache, f, indent=4)

    def set_topic(self, topic):
        self.topic = topic
        if self.topic in self.topic_parameters:
            self.keywords = self.topic_parameters[self.topic]["keywords"]
            self.people_uris = self.topic_parameters[self.topic]["people_uris"]
            self.orgs_uris = self.topic_parameters[self.topic]["orgs_uris"]
            self.source_location_uri = self.topic_parameters[self.topic]["source_location_uri"]
        else:
            raise ValueError(f"Topic not found. The available topics are: {self.available_topics}")

    def map_sentiment_to_string(self, sentiment_score):
        if sentiment_score is None:
            return "neutral"
        elif sentiment_score > 0.1:
            return "positive"
        elif sentiment_score < -0.1:
            return "negative"
        else:
            return "neutral"

    def get_articles(self, start_date, end_date, sentiment=None, limit=5):
        cache_key = f"{self.topic}_{start_date}_{end_date}_{sentiment}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        all_uris = self.people_uris + self.orgs_uris
        query = QueryArticlesIter(
            dateStart=start_date,
            dateEnd=end_date,
            lang="eng",
            keywords=QueryItems.OR(self.keywords),
            conceptUri=QueryItems.OR(all_uris),
            locationUri=QueryItems.OR(self.source_location_uri),
            keywordsLoc="body,title",
            isDuplicateFilter="skipDuplicates"
        )

        articles = []
        count = 0
        retries = 0

        while retries < MAX_RETRIES:
            try:
                for article in query.execQuery(self.er, sortBy="socialScore", sortByAsc=False):
                    try:
                        article_sentiment = article.get("sentiment")
                        if isinstance(article_sentiment, dict):
                            article_sentiment = article_sentiment.get("body", None)
                        elif not isinstance(article_sentiment, float):
                            article_sentiment = None

                        sentiment_label = self.map_sentiment_to_string(article_sentiment)

                        article_date = article.get("date")
                        article_title = article.get("title")
                        article_body = article.get("body")
                        article_url = article.get("url")

                        if sentiment and sentiment_label != sentiment:
                            continue

                        if not all([article_date, article_title, article_body, article_url]):
                            print("WARNING: Skipping article due to missing essential fields.")
                            continue

                        articles.append({
                            "date": article_date,
                            "title": article_title,
                            "body": article_body,
                            "url": article_url,
                            "sentiment": sentiment_label
                        })

                        count += 1
                        if count >= limit:
                            break

                    except Exception as e:
                        print(f"ERROR: Failed to process article: {article}. Exception: {e}")

                print(f"Total articles retrieved: {len(articles)}")
                if articles:
                    print(f"Date range of retrieved articles: {articles[0]['date']} to {articles[-1]['date']}")
                
                self.cache[cache_key] = articles
                self.save_cache()
                return articles

            except Exception as e:
                retries += 1
                logging.error(f"Attempt {retries}/{MAX_RETRIES} - Failed to process articles: {e}")
                if retries < MAX_RETRIES:
                    time.sleep(RETRY_WAIT_TIME)
                else:
                    logging.error("Failed to retrieve articles after 3 attempts.")

        return []

    def save_articles(self, articles_by_topic, output_path="../data/processed/articles.json"):
        Path(output_path).write_text(json.dumps(articles_by_topic, indent=4))

def main():
    news = News()
    start_date = "2022-01-01"
    end_date = "2024-08-01"
    articles_by_topic = {}

    for topic in news.available_topics:
        news.set_topic(topic)
        articles_by_topic[topic] = {
            "positive": news.get_articles(start_date, end_date, sentiment="positive"),
            "negative": news.get_articles(start_date, end_date, sentiment="negative")
        }

    news.save_articles(articles_by_topic)

if __name__ == "__main__":
    main()
