import logging
import re
from difflib import get_close_matches

class CustomOutputParser:
    def __init__(self):
        self.target_keys = {
            'relevance': ['Relevance', 'Rel', 'Importance'],
            'sentiment': ['Sentiment', 'Feelings', 'Opinion'],
            'agreement': ['Agreement', 'Consensus', 'Alignment', "Agree", "Disagree", "Disagreement"],
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
        section_header_pattern = re.compile(r"^\s*\*\*(.*?)\*\*$")
        inline_section_pattern = re.compile(r"^\s*\*\*(.*?)\*\* (.*)$")
        kv_pattern = re.compile(r"^\s*[*-]\s*([\w\s]+):\s*(.+)$")
        simple_kv_pattern = re.compile(r"^\s*([\w\s]+):\s*(.+)$")

        twitter_post_start = False
        twitter_post_content = []

        for line in text.split('\n'):
            # Match inline sections
            inline_match = inline_section_pattern.match(line)
            kv_match = kv_pattern.match(line)
            simple_kv_match = simple_kv_pattern.match(line)

            if inline_match:
                current_section = inline_match.group(1).strip()
                sections[current_section] = inline_match.group(2).strip()
                current_section = None
            elif kv_match:
                key = kv_match.group(1).strip()
                value = kv_match.group(2).strip()
                sections[key] = value
            elif simple_kv_match:
                key = simple_kv_match.group(1).strip()
                value = simple_kv_match.group(2).strip()
                sections[key] = value
            else:
                header_match = section_header_pattern.match(line)
                if header_match:
                    current_section = header_match.group(1).strip()
                    sections[current_section] = ""
                elif current_section:
                    sections[current_section] += line + "\n"

                # Check for Twitter Post start
                if re.match(r".*Twitter Post.*:", line, re.IGNORECASE):
                    twitter_post_start = True
                    twitter_post_content.append(line.split(":", 1)[1].strip())
                    continue
                
                if twitter_post_start:
                    if line.strip() == "" and twitter_post_content:
                        twitter_post_start = False
                    else:
                        twitter_post_content.append(line.strip())

        sections = {key: value.strip() for key, value in sections.items()}

        if twitter_post_content:
            sections["Twitter Post"] = " ".join(twitter_post_content).strip('"').strip()

        return sections

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
