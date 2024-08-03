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

def generate_article_prompt(question, article, previous_response):
    prompt = f"""
Here are your previous responses to the same question:
- Relevance: {previous_response['relevance']}
- Sentiment: {previous_response['sentiment']}
- Agreement: {previous_response.get('agreement', 'N/A')}
- Twitter Post: {previous_response['twitter_post']}

Now, read the following article:

Title: {article['title']}
Date: {article['date']}
URL: {article['url']}

{article['body']}

Now, provide your response to the question again.

Question:
"{question}"
    - Relevance: [1-5]
    - Sentiment: [1-5]
    - Agreement: [1-5]
    - Twitter Post:
"""
    return prompt

def save_responses(output_file, responses):
    if Path(output_file).exists():
        with open(output_file, 'r') as file:
            existing_data = json.load(file)
            responses = existing_data + responses
    else:
        existing_data = []

    with open(output_file, 'w') as outfile:
        json.dump(responses, outfile, indent=4)

def main():
    persona_prompts = load_json_file('../data/processed/persona_prompts.json')
    before_responses = load_json_file('../data/processed/before_responses.json')
    articles_by_topic = load_json_file('../data/processed/articles.json')
    question_to_topic = load_json_file('../data/raw/question_to_topic.json')["question_to_topic"]

    llm = CustomLLM(model="llama3.1:70b-instruct-q6_K", api_url="https://inf.cl.uni-trier.de/")
    parser = CustomOutputParser()

    questions = list(question_to_topic.keys())

    after_responses_file = '../data/processed/after_responses.json'
    processed_ids = set()
    if Path(after_responses_file).exists():
        with open(after_responses_file, 'r') as file:
            data = json.load(file)
            processed_ids = {entry['user_id'] for entry in data}

    before_responses_dict = {(resp['user_id'], resp['question']): resp['response'] for resp in before_responses}

    all_responses = []
    checkpoint_counter = 0

    for persona in persona_prompts:
        persona_prompt = persona["persona_prompt"]
        user_id = persona["user_id"]

        if user_id in processed_ids:
            continue

        user_responses = []

        for question in questions:
            if (user_id, question) not in before_responses_dict:
                continue

            parsed_output = before_responses_dict[(user_id, question)]
            relevance = int(parsed_output['relevance'])
            sentiment = int(parsed_output['sentiment'])
            agreement = parsed_output.get('agreement', 'N/A')
            try:
                agreement_int = int(agreement) if isinstance(agreement, str) and agreement.isdigit() else agreement
            except ValueError:
                agreement_int = None

            if relevance <= 2 and sentiment <= 2 and (agreement_int is None or (isinstance(agreement_int, int) and agreement_int <= 2)):
                topic = question_to_topic.get(question)
                if not topic or topic not in articles_by_topic:
                    continue

                articles = articles_by_topic[topic]
                opposing_sentiment = "positive" if sentiment <= 2 else "negative"
                relevant_articles = articles[opposing_sentiment]

                for article in relevant_articles:
                    article_prompt = generate_article_prompt(question, article, parsed_output)
                    raw_response = llm.generate_response(persona_prompt, article_prompt)
                    logging.info(f"Raw response for user_id {user_id}, question '{question}': {raw_response}")

                    revised_parsed_output = parser.parse(raw_response)
                    user_responses.append({
                        "user_id": user_id,
                        "question": question,
                        "article": {
                            "title": article['title'],
                            "date": article['date'],
                            "url": article['url'],
                            "body": article['body'],
                            "sentiment": article['sentiment']
                        },
                        "response": revised_parsed_output
                    })

        all_responses.extend(user_responses)
        processed_ids.add(user_id)
        checkpoint_counter += 1

        if checkpoint_counter % 5 == 0:
            save_responses(after_responses_file, all_responses[-5*len(questions):])

    if checkpoint_counter % 5 != 0:
        save_responses(after_responses_file, all_responses[-(checkpoint_counter % 5)*len(questions):])

if __name__ == '__main__':
    main()
