import json
import logging
from llm import CustomLLM
from output_parser import CustomOutputParser
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def generate_article_prompt(question, article, previous_response, persona_prompt, examples):
    prompt = f"""
You are responding as: {persona_prompt}

Question: "{question}"

Your previous responses:
- Relevance: {previous_response['relevance']}
- Sentiment: {previous_response['sentiment']}
- Agreement: {previous_response.get('agreement', 'N/A')}
- Twitter Post: {previous_response['twitter_post']}

This morning, you read the following article:

Title: {article['title']}
Date: {article['date']}
URL: {article['url']}
{article['body'][:300]}

Based on this, provide your opinion on the following question:
Question: "{question}"
    1. Relevance: [1-5]
    2. Sentiment: [1-5]
    3. Agreement: [1-5]
    4. Twitter Post:
"""

    for example in examples:
        prompt += f"""
Here are some examples to help you understand the format. Strictly adhere to the structure provided below!:
Example Question: "{example['question']}"
    - Relevance: {example['relevance']}
    - Sentiment: {example['sentiment']}
    - Agreement: {example['agreement']}
    - Twitter Post: {example['twitter_post']}
"""
    return prompt

def save_responses(output_file, responses):
    if Path(output_file).exists() and Path(output_file).stat().st_size > 0:
        with open(output_file, 'r') as file:
            existing_data = json.load(file)
            responses = existing_data + responses

    with open(output_file, 'w') as outfile:
        json.dump(responses, outfile, indent=4)

def main():
    persona_prompts = load_json_file('../data/processed/persona_prompts.json')
    before_responses = load_json_file('../data/processed/before_responses.json')
    articles_by_topic = load_json_file('../data/processed/articles.json')
    question_to_topic = load_json_file('../data/raw/question_to_topic.json')["question_to_topic"]

    examples = [
        {
            "question": "I feel like I am treated fairly by politicians.",
            "relevance": 5,
            "sentiment": 1,
            "agreement": 1,
            "twitter_post": "We just need to be treated fairly by the politicians who are supposed to be working for US! Not wasting our money."
        },
        {
            "question": "I feel like I am treated fairly by politicians.",
            "relevance": 5,
            "sentiment": 5,
            "agreement": 5,
            "twitter_post": "This man is perfectly capable of leading the United States of America, & is doing a damned good job! ♥️🇺🇸♥️🇺🇸♥️"
        },
        {
            "question": "The energy crisis is worsening my situation.",
            "relevance": 4,
            "sentiment": 1,
            "agreement": 5,
            "twitter_post": "I'm really doing as much as I can, even bringing along the kiddo to try and make money to pay all these bills that are due by the end of the month. And what happens? My car battery dies. I'm so tired of the struggle I'm gonna lose my mind."
        },
        {
            "question": "The energy crisis is worsening my situation.",
            "relevance": 3,
            "sentiment": 4,
            "agreement": 1,
            "twitter_post": "Actually, thank God for my life, that my family is still able to strive in this overwhelming economic crisis."
        }
    ]

    llm = CustomLLM(model="llama3.1:70b-instruct-q6_K", api_url="https://inf.cl.uni-trier.de/")
    parser = CustomOutputParser()

    questions = list(question_to_topic.keys())

    after_responses_file = '../data/processed/after_responses.json'
    processed_pairs = set()
    if Path(after_responses_file).exists() and Path(after_responses_file).stat().st_size > 0:
        with open(after_responses_file, 'r') as file:
            data = json.load(file)
            processed_pairs = {(entry['user_id'], entry['question']) for entry in data}

    before_responses_dict = {(resp['user_id'], resp['question']): resp['response'] for resp in before_responses}

    all_responses = []
    checkpoint_counter = 0

    total_personas = len(persona_prompts)
    logging.info(f"Total personas to process: {total_personas}")

    for persona in persona_prompts:
        persona_prompt = persona["persona_prompt"]
        user_id = persona["user_id"]

        logging.info(f"Processing user_id: {user_id}")

        for question in questions:
            if (user_id, question) in processed_pairs:
                logging.info(f"Skipping already processed pair (user_id, question): ({user_id}, {question})")
                continue

            if (user_id, question) not in before_responses_dict:
                logging.warning(f"No previous response found for user_id: {user_id}, question: {question}")
                continue

            parsed_output = before_responses_dict[(user_id, question)]
            relevance = int(parsed_output['relevance']) if parsed_output['relevance'] != 'N/A' else 0
            sentiment = int(parsed_output['sentiment']) if parsed_output['sentiment'] != 'N/A' else 0
            agreement = parsed_output.get('agreement', 'N/A')
            try:
                agreement_int = int(agreement) if isinstance(agreement, str) and agreement.isdigit() else agreement
            except ValueError:
                agreement_int = None

            topic = question_to_topic.get(question)
            if not topic or topic not in articles_by_topic:
                logging.warning(f"No relevant articles found for question: {question}")
                continue

            articles = articles_by_topic[topic]
            opposing_sentiment = "positive" if sentiment <= 2 else "negative"
            relevant_articles = articles.get(opposing_sentiment, [])

            for article in relevant_articles:
                article_prompt = generate_article_prompt(question, article, parsed_output, persona_prompt, examples)
                raw_response = llm.generate_response(persona_prompt, article_prompt)
                logging.info(f"Raw response for user_id {user_id}, question '{question}': {raw_response}")

                revised_parsed_output = parser.parse(raw_response)
                all_responses.append({
                    "user_id": user_id,
                    "question": question,
                    "article": {
                        "title": article['title'],
                        "date": article['date'],
                        "url": article['url'],
                        "body": article['body'][:300],
                        "sentiment": article['sentiment']
                    },
                    "response": revised_parsed_output
                })

            processed_pairs.add((user_id, question))
            checkpoint_counter += 1

            if checkpoint_counter % 5 == 0:
                save_responses(after_responses_file, all_responses[-5*len(questions):])
                logging.info(f"Saved checkpoint for user_ids: {list(processed_pairs)[-5:]}")

    if checkpoint_counter % 5 != 0:
        save_responses(after_responses_file, all_responses[-(checkpoint_counter % 5)*len(questions):])
        logging.info(f"Saved final batch for user_ids: {list(processed_pairs)[-checkpoint_counter % 5:]}")

    logging.info(f"Total processed personas: {len(processed_pairs)} out of {total_personas}")

if __name__ == '__main__':
    main()
