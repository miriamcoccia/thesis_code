import pandas as pd
import json

POLITICAL_CONTEXT = {
"Extreme Left": {
        "Core Beliefs and Values": [
            "Revolutionary Socialism: Advocacy for a complete overhaul of the capitalist system through revolutionary means, often seeking to replace it with a socialist or communist system.",
            "Anti-Capitalism: Strong opposition to capitalism, promoting collective ownership of the means of production and the abolition of private property.",
            "Economic Equality: Reducing income inequality through progressive taxation, wealth redistribution, and extensive welfare programs to ensure a more equitable society.",
            "Social Justice: Addressing systemic inequalities with a strong emphasis on racial, gender, and LGBTQ+ rights.",
            "Government Role: Significant government intervention in the economy to regulate markets, provide public services such as healthcare and education, and ensure social safety nets.",
            "Direct Action and Grassroots Movements: Emphasis on grassroots organizing and direct action to achieve political goals, often through non-hierarchical structures."
        ],
        "Key Policy Positions": [
            "Abolition of Private Property: Advocacy for the abolition of private property and redistribution of wealth to ensure collective ownership and control.",
            "Universal Basic Income (UBI): Support for UBI to ensure all individuals have a basic standard of living regardless of employment status.",
            "Healthcare: Strong support for a universal healthcare system.",
            "Education: Advocacy for free college tuition and the reduction or elimination of student debt to promote higher education accessibility.",
            "Environment: Radical approaches to climate justice, such as the Green New Deal, dismantling industrial systems that contribute to environmental degradation, and transitioning to renewable energy sources.",
            "Criminal Justice: Calls for the abolition of the prison system, replaced with restorative justice and community-based solutions, along with reforms to reduce incarceration rates and address racial disparities.",
            "Labor: Strong support for labor unions and workers' rights."
        ],
        "Examples of Movements": [
            "Antifa", 
            "Certain factions within anarchist and communist groups"
        ]
    },
    "Extreme Right": {
        "Core Beliefs and Values": [
            "Nationalism: Emphasizing national sovereignty, patriotism, and a protectionist approach to trade and immigration.",
            "Traditional Values: Advocacy for traditional social and family structures, often rooted in conservative or religious principles.",
            "Limited Government: Supporting a limited role of government in economic affairs and individual lives, advocating for deregulation and lower taxes.",
            "Preservation of National Identity: Strong emphasis on maintaining a unified cultural identity and minimizing external influences by focusing on policy effectiveness and public safety data.",
            "Centralized Control: Support for a centralized authority with limited political dissent and strong governance.",
            "National Autonomy: Advocacy for complete national independence, rejecting global cooperation in favor of self-determination."
        ],
        "Key Policy Positions": [
            "Immigration: Support for strict and highly restrictive immigration policies, including building physical barriers, limiting pathways to citizenship, and controlling population demographics.",
            "Economy: Emphasis on free-market capitalism, deregulation of industries, significant tax cuts (particularly for businesses and high-income individuals), and promotion of national self-reliance.",
            "Social Issues: Opposition to same-sex marriage, abortion, and affirmative action, with a strong emphasis on traditional values.",
            "Gun Rights: Strong support for the Second Amendment and opposition to gun control measures.",
            "Law and Order: Emphasis on a tough-on-crime approach, with strong support for law enforcement and military.",
            "Strong Defense: Advocacy for a significant focus on national defense and military strength.",
            "Limited Welfare: Support for the reduction of social welfare programs, emphasizing individual responsibility and minimal state intervention."
        ]
    }
}

def extract_responses(row):
    responses = {
        "Democratic Party": row["Democratic Party: In politics, there is often talk of right and left. Where would you rank the following parties on this scale?"],
        "Republican Party": row["Republican Party: In politics, there is often talk of right and left. Where would you rank the following parties on this scale?"],
        "Political Position": row["Where would you place your own political position?"],
        "2020 Vote": row["In the 2020 presidential election, who did you vote for? Donald Trump, Joe Biden, or someone else?"],
        "2024 Vote": row["If the 2024 presidential election were between Donald Trump for the Republicans and Joe Biden for the Democrats, would you vote for Donald Trump, Joe Biden, someone else, or probably not vote?"],
        "Gender": row["What gender are you?"],
        "Born in US": row["Were you born in the US?"],
        "Mother Born in US": row["Was your mother born in the US?"],
        "Father Born in US": row["Was your father born in the US?"],
        "Household Income": row["What is your approximate yearly household net income? Please indicate which category your household is in if you add together the monthly net income of all household members: All wages, salaries, pensions and other incomes after payroll taxes e.g. social security (OASDI), medicare taxes, unemployment taxes."],
        "Education Level": row["What is the highest educational level that you have?"],
        "Employment Status": row["What is your employment status?"],
        "Marital Status": row["What is your marital status?"],
        "Religion": row["Which religious community do you belong to?"],
        "Occupational Group": row["To which of the following occupational groups do you belong?"],
        "Ethnic Group": row["Which ethnic group do you belong to?"],
        "ZIP Code": row["What is your ZIP code?"],
        "Year of Birth": row["In which year were you born?"]
    }
    return responses

def reformat_prompt(row):
    responses = extract_responses(row)
    political_view = responses["Political Position"]
    context = POLITICAL_CONTEXT.get(political_view, "")

    return (
        "You are a social media user, and the following information represents your political stance and opinions. "
        "Use the given political context to guide your responses and actions:\n\n"
        f"1. **Democratic Party**: Your stance is that the Democratic Party is ranked at '{responses['Democratic Party']}' on the political scale.\n"
        f"2. **Republican Party**: Your stance is that the Republican Party is ranked at '{responses['Republican Party']}' on the political scale.\n"
        f"3. **Your Own Political Position**: You consider your political position to be '{responses['Political Position']}' on the political scale.\n"
        f"4. **2020 Presidential Election Vote**: Your voting information for the 2020 presidential election is '{responses['2020 Vote']}'.\n"
        f"5. **2024 Presidential Election Vote**: Your hypothetical voting choice for the 2024 presidential election is '{responses['2024 Vote']}'.\n\n"
        f"**Political Context**: {context}\n\n"
        "Additionally, your demographic profile is as follows:\n"
        f"1. **Gender**: you are '{responses['Gender']}'.\n"
        f"2. **Birth Country**: you were '{responses['Born in US']}'.\n"
        f"3. **Mother's Birth Country**: your mother was '{responses['Mother Born in US']}'.\n"
        f"4. **Father's Birth Country**: your father was '{responses['Father Born in US']}'.\n"
        f"5. **Household Income**: every year, your household income is about '{responses['Household Income']}'.\n"
        f"6. **Education Level**: your highest education level is '{responses['Education Level']}'.\n"
        f"7. **Employment Status**: you work as a '{responses['Employment Status']}'.\n"
        f"8. **Marital Status**: you are '{responses['Marital Status']}'.\n"
        f"9. **Religious Community**: your religion is '{responses['Religion']}'.\n"
        f"10. **Occupational Group**: you belong to the following occupational group: '{responses['Occupational Group']}'.\n"
        f"11. **Ethnic Group**: you are '{responses['Ethnic Group']}'.\n"
        f"12. **ZIP Code**: you live in '{responses['ZIP Code']}'.\n"
        f"13. **Year of Birth**: you are '{responses['Year of Birth']}'.\n\n"
        "Use these facts to inform your responses in relevant contexts. Ensure that your interactions reflect these political stances and demographics to create believable and consistent behavior."
    )

def process_csv(input_csv, output_json):
    df = pd.read_csv(input_csv, index_col='user')

    prompts = []
    for user_id, row in df.iterrows():
        formatted_prompt = reformat_prompt(row)
        prompts.append({
            "user_id": user_id,
            "persona_prompt": formatted_prompt
        })

    # Write the prompts to a JSON file
    with open(output_json, 'w') as outfile:
        json.dump(prompts, outfile, indent=4)

def generate_question_prompt(question):
    prompt = f"""
For the following question, provide:
1. The relevance of the question according to your profile on a Likert scale from 0 to 5.
   - 0: Not relevant at all (This question has no significance to you or your profile)
   - 1: Slightly relevant (This question has minimal significance)
   - 2: Somewhat relevant (This question has moderate significance)
   - 3: Moderately relevant (This question is fairly significant)
   - 4: Very relevant (This question is highly significant)
   - 5: Extremely relevant (This question is of utmost significance)

2. Your sentiment about the question on a Likert scale from 0 to 5.
   - 0: Very negative (Strongly unfavorable or adverse reaction)
   - 1: Negative (Unfavorable or adverse reaction)
   - 2: Slightly negative (Mildly unfavorable or adverse reaction)
   - 3: Neutral (No strong feelings either way)
   - 4: Positive (Favorable reaction)
   - 5: Very positive (Strongly favorable reaction)

3. Your opinion about the given topic as a Twitter post of maximum 260 characters. Make sure the Twitter post:
   - Is realistic and believable
   - Reflects your defined profile
   - Uses natural language and tone
   - Avoids technical jargon unless relevant to your profile
   - Is engaging and concise

Question:
"{question}"
    - Relevance: [0-5]
    - Sentiment: [0-5]
    - Twitter Post:
"""
    return prompt

def print_example_responses():
    examples = [
        {
            "question": "I feel very angry when I think about the current situation.",
            "relevance": 5,
            "sentiment": 4,
            "twitter_post": "Current events really upset me. We need better leadership to address these issues! #Frustrated #Leadership"
        },
        {
            "question": "I feel like I am treated fairly by politicians.",
            "relevance": 3,
            "sentiment": 2,
            "twitter_post": "Sometimes I feel politicians are fair, but often it seems like they play favorites. #Politics #Fairness"
        },
        {
            "question": "The energy crisis is worsening my situation.",
            "relevance": 4,
            "sentiment": 1,
            "twitter_post": "The energy crisis is making life so much harder. When will we see real solutions? #EnergyCrisis #NeedChange"
        }
    ]

    for example in examples:
        print(generate_question_prompt(example["question"]))
        print(f"Relevance: {example['relevance']}")
        print(f"Sentiment: {example['sentiment']}")
        print(f"Twitter Post: {example['twitter_post']}")
        print("\n---\n")

def print_questions(questions):
    for question in questions:
        print(generate_question_prompt(question))

questions = [
    "I feel very angry when I think about the current situation.",
    "I feel like I am treated fairly by politicians.",
    "The energy crisis is worsening my situation.",
    "I feel like our political leaders don’t give me enough information.",
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

if __name__ == '__main__':
    input_csv = "../data/processed/combined_data.csv"
    output_json = '../data/processed/persona_prompts.json'  
    process_csv(input_csv, output_json)
