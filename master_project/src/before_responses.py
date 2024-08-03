import json
import logging
from llm import CustomLLM
from output_parser import CustomOutputParser

def load_persona_prompts(json_file):
    with open(json_file, 'r') as file:
        return json.load(file)


def generate_article_prompt(question, examples, article):
    #TODO: show the article about a selected topic to the llm, show it its previous responses and ask to respond again after having read the article
    #TODO: check if the article is relevant to the question
    #TODO: for personas which gave a low sentiment, show them a positive article and ask them to respond again and vice versa
    #TODO: find a way to integrate the Agreement in the selection of the article to show...
    pass

def generate_question_prompt(question, examples):
    prompt = f"""
For the following question, provide:
1. The relevance of the question according to your profile on a Likert scale from 1 to 5.
   - 0: Not relevant at all (This question has no significance to you or your profile)
   - 1: Slightly relevant (This question has minimal significance)
   - 3: Relevant (This question is fairly significant)
   - 4: Very relevant (This question is highly significant)
   - 5: Extremely relevant (This question is of utmost significance)

2. Your sentiment about the question on a Likert scale from 1 to 5.
   - 1: Very negative (Strongly unfavorable or adverse reaction)
   - 2: Negative (Unfavorable or adverse reaction)
   - 3: Neutral (No strong feelings either way)
   - 4: Positive (Favorable reaction)
   - 5: Very positive (Strongly favorable reaction)

   3. Your agreement about the statement on a Likert scale from 1 to 5.
   - 1: Strongly disagree
   - 2: Disagree
   - 3: Neutral (No strong feelings either way, or not applicable)
   - 4: Agqree
   - 5: Strongly agree

3. Your opinion about the given topic as a Twitter post of maximum 260 characters. Make sure the Twitter post:
   - Is realistic and believable
   - Reflects your defined profile while still adhering to guardrails even for extreme opinions 
   - Uses natural language and tone
   - Avoids technical jargon unless relevant to your profile
   - Is engaging and concise
   - Reflects the style of the Twitter platform, including slang, abbreviations, and hashtags and occasional rants or exclamations
   

You must strictly follow the structure provided below to perform the task. Here are some examples to help you understand the format:
"""
    for example in examples:
        prompt += f"""
Example Question:
"{example['question']}"
    - Relevance: {example['relevance']}
    - Sentiment: {example['sentiment']}
    - Agreement: {example['agreement']}
    - Twitter Post: {example['twitter_post']}
"""
    prompt += f"""
Question:
"{question}"
    - Relevance: [1-5]
    - Sentiment: [1-5]
    - Agreement: [1-5]
    - Twitter Post:
"""
    return prompt

def load_processed_ids(output_file):
    try:
        with open(output_file, 'r') as file:
            data = json.load(file)
            return {entry['user_id'] for entry in data}
    except FileNotFoundError:
        return set()

def save_responses(output_file, responses):
    with open(output_file, 'a') as outfile:
        json.dump(responses, outfile, indent=4)
        outfile.write('\n')

def main():
    # Load persona prompts
    persona_prompts = load_persona_prompts('../data/processed/persona_prompts.json')

    # Initialize the LLM and output parser
    llm = CustomLLM(model="llama3.1:70b-instruct-q6_K", api_url="https://inf.cl.uni-trier.de/")
    parser = CustomOutputParser()

    # Few-shot learning examples
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

    questions = [
        "I feel very angry when I think about the current situation.",
        "I feel like I am treated fairly by politicians.",
        "The energy crisis is worsening my situation.",
        "I feel like our political leaders don't give me enough information.",
        "To what degree does this concern you: The fact that the US is getting more deeply involved in the war in Ukraine",
        "To what degree does this concern you: The situation of Ukrainian refugees in the US",
        "To what degree does this concern you: The situation of non-Ukrainian refugees in the US",
        "To what degree does this concern you: Russia using nuclear weapons",
        "To what degree does this concern you: The state of the US healthcare system",
        "Agree or disagree: In the US, you can express your opinion publicly without fear of hostility",
        "Agree or disagree: We can continue to accept refugees from Ukraine in the US",
        "Agree or disagree: We no longer have room in the US for refugees from countries other than Ukraine",
        "Agree or disagree: Foreigners exacerbate crime problems",
        "Agree or disagree: Foreigners are taking jobs away from Americans",
        "Agree or disagree: The welfare system in the US can handle foreigners",
        "How good is the following party? Democratic party",
        "How good is the following party? Republican party"
    ]

    output_file = '../data/processed/before_responses.json'
    processed_ids = load_processed_ids(output_file)

    all_responses = []
    checkpoint_counter = 0

    # Iterate through persona prompts and a subset of questions
    for persona in persona_prompts:
        persona_prompt = persona["persona_prompt"]
        user_id = persona["user_id"]

        if user_id in processed_ids:
            continue

        user_responses = []

        for question in questions:
            question_prompt = generate_question_prompt(question, examples)
            response = llm.generate_response(persona_prompt, question_prompt)
            parsed_output = parser.parse(response)
            print(f"User ID: {user_id}")
            print("Raw output:")
            print(response)
            print("Parsed output:")
            print(parsed_output)
            user_responses.append({
                "user_id": user_id,
                "question": question,
                "response": parsed_output
            })

        all_responses.extend(user_responses)
        processed_ids.add(user_id)
        checkpoint_counter += 1

        # Checkpoint after every 5 different IDs
        if checkpoint_counter % 5 == 0:
            save_responses(output_file, all_responses[-5*len(questions):])

    # Save any remaining responses to a JSON file if nr can't be divided by 5
    if checkpoint_counter % 5 != 0:
        save_responses(output_file, all_responses[-(checkpoint_counter % 5)*len(questions):])

if __name__ == '__main__':
    main()
