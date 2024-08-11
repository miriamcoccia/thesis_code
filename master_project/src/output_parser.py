import logging
import re
from difflib import get_close_matches

class CustomOutputParser:
    def __init__(self):
        self.target_keys = {
            'relevance': ['Relevance', 'Rel', 'Importance'],
            'sentiment': ['Sentiment', 'Feelings', 'Opinion'],
            'agreement': ['Agreement', 'Consensus', 'Alignment', 'Agree', 'Disagree', 'Disagreement'],
            'twitter_post': ['Twitter Post', 'Tweet', 'Social Post', 'Message', 'TwitterPost']
        }

    def parse(self, output: str) -> dict:
        try:
            parsed_data = self.extract_sections(output)
            logging.debug(f"Extracted sections: {parsed_data}")

            relevance = self.find_closest_value(parsed_data, self.target_keys['relevance'])
            sentiment = self.find_closest_value(parsed_data, self.target_keys['sentiment'])
            agreement = self.find_closest_value(parsed_data, self.target_keys['agreement'])
            twitter_post = self.find_closest_value(parsed_data, self.target_keys['twitter_post'])

            if relevance is None:
                logging.warning("Relevance field not found in the output.")
                relevance = "N/A"
            if sentiment is None:
                logging.warning("Sentiment field not found in the output.")
                sentiment = "N/A"
            if agreement is None:
                logging.warning("Agreement field not found in the output.")
                agreement = "N/A"
            if twitter_post is None:
                logging.warning("Twitter Post field not found in the output.")
                twitter_post = "N/A"

            return {
                "type": "final_answer",
                "relevance": self.extract_numeric_value(relevance),
                "sentiment": self.extract_numeric_value(sentiment),
                "agreement": self.extract_numeric_value(agreement),
                "twitter_post": twitter_post.strip().strip('"')
            }
        except Exception as e:
            logging.error(f"Error parsing LLM output: {e}")
            return {"type": "raw_output", "content": output.strip()}

    def extract_sections(self, text: str) -> dict:
        sections = {}
        current_section = None
        twitter_post_start = False
        twitter_post_content = []

        section_patterns = [
            re.compile(r"^\s*[*-]+\s*([A-Za-z\s]+):\s*(.*)$"),  # * Key: Value or - Key: Value
            re.compile(r"^\s*\d+\.\s*([A-Za-z\s]+):\s*(.*)$"),  # 1. Key: Value
            re.compile(r"^\s*([A-Za-z\s]+):\s*(.*)$"),  # Key: Value
            re.compile(r"^\s*\*\*+\s*([A-Za-z\s]+)\s*\*\*+\s*:\s*(.*)$"),  # **Key**: Value
        ]

        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            matched = False
            for pattern in section_patterns:
                match = pattern.match(line)
                if match:
                    key = match.group(1).strip()
                    value = match.group(2).strip()
                    sections[key] = value
                    if key.lower() in map(str.lower, self.target_keys['twitter_post']):
                        twitter_post_start = True
                    matched = True
                    break

            if not matched and twitter_post_start:
                twitter_post_content.append(line)

        if twitter_post_content:
            sections["Twitter Post"] = " ".join(twitter_post_content).strip('"').strip()

        return {key: value.strip() for key, value in sections.items()}

    def find_closest_value(self, sections: dict, target_keys: list) -> str:
        for key in target_keys:
            closest_key = self.find_closest_key(sections.keys(), [key])
            if closest_key:
                return sections[closest_key]
        return None

    def find_closest_key(self, keys, target_keys):
        all_keys = list(keys)
        for target in target_keys:
            closest_matches = get_close_matches(target, all_keys, n=1, cutoff=0.6)
            if closest_matches:
                return closest_matches[0]
        return None

    def extract_numeric_value(self, text: str) -> int:
        if text and isinstance(text, str):
            match = re.search(r'\d+', text)
            if match:
                return int(match.group(0))
        return "N/A"

class OutputParserException(Exception):
    pass

# Ensure logging is set up to show debug information
logging.basicConfig(level=logging.DEBUG)
