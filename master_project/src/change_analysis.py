import json
from pathlib import Path

def load_json(file_path):
    return json.loads(Path(file_path).read_text())

def to_int(value):
    if value is None or value == "N/A":
        return 0
    return int(value)

def calculate_shifts(before, after):
    shifts = []
    
    # Create a lookup table for before responses by user_id and question
    before_lookup = {(entry["user_id"], entry["question"]): entry["response"] for entry in before}

    for entry in after:
        user_id = entry["user_id"]
        question = entry["question"]
        article_title = entry["article"]["title"]
        article_sentiment = entry["article"]["sentiment"]
        
        # Find the corresponding before response
        before_response = before_lookup.get((user_id, question))
        if not before_response:
            continue  # Skip if there's no matching before response

        after_response = entry["response"]

        # Calculate shifts using nested response fields with safe access
        relevance_shift = to_int(after_response.get("relevance")) - to_int(before_response.get("relevance"))
        sentiment_shift = to_int(after_response.get("sentiment")) - to_int(before_response.get("sentiment"))
        agreement_shift = (
            to_int(after_response.get("agreement")) - to_int(before_response.get("agreement"))
            if "agreement" in before_response and "agreement" in after_response else None
        )

        shift_entry = {
            "user_id": user_id,
            "question": question,
            "article_title": article_title,
            "article_sentiment": article_sentiment,
            "relevance_shift": relevance_shift,
            "sentiment_shift": sentiment_shift,
            "agreement_shift": agreement_shift
        }
        shifts.append(shift_entry)
    
    return shifts

def main():
    before_responses = load_json("../data/processed/before_responses.json")
    after_responses = load_json("../data/processed/after_responses.json")
    
    shifts = calculate_shifts(before_responses, after_responses)
    
    # Save the shifts to a JSON file
    Path("../data/processed/shifts.json").write_text(json.dumps(shifts, indent=4))

if __name__ == "__main__":
    main()
