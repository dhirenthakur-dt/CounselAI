import re
import string
from rapidfuzz import fuzz

STOP_WORDS = [
    'college', 'institute', 'engineering', 'technology', 'and', 'of', 'the',
    'autonomous', 'university', 'campus', 'trust', 'society', 'maharaj',
    'shikshan', 'prasarak', 'mandal', 'group', 'institutions'
]

def normalize_name(name):
    if not isinstance(name, str):
        return ""
    # Lowercase
    name = name.lower()
    # Remove punctuation
    name = name.translate(str.maketrans('', '', string.punctuation))
    # Remove stop words
    words = name.split()
    filtered_words = [w for w in words if w not in STOP_WORDS]
    # Rejoin
    return ' '.join(filtered_words).strip()

def calculate_confidence(input_name, scraped_name):
    norm_input = normalize_name(input_name)
    norm_scraped = normalize_name(scraped_name)
    
    if not norm_input or not norm_scraped:
        return 0.0

    # RapidFuzz metrics
    token_sort = fuzz.token_sort_ratio(norm_input, norm_scraped)
    token_set = fuzz.token_set_ratio(norm_input, norm_scraped)
    partial_ratio = fuzz.partial_ratio(norm_input, norm_scraped)
    q_ratio = fuzz.QRatio(norm_input, norm_scraped)
    
    # Weighted average or max of some
    # Token set is very good for out-of-order words but can overestimate
    # We will take an average to get a balanced confidence score
    confidence = (token_sort + token_set + partial_ratio + q_ratio) / 4.0
    
    # Give a boost if one is exactly inside the other after normalization
    if norm_input in norm_scraped or norm_scraped in norm_input:
        confidence = max(confidence, 90.0)

    return round(confidence, 2)

def is_valid_match(input_name, scraped_name, state=""):
    # First check state if available (in our case it's actually address)
    if state and 'maharashtra' not in state.lower():
        return False, 0.0
        
    confidence = calculate_confidence(input_name, scraped_name)
    
    # We also do a check to reject distinct false positives
    # For instance, Govt College of Engineering Aurangabad vs Gandhinagar
    # Since Gandhinagar is in Gujarat, the state check will catch it.
    # But let's add basic keyword strictness for cities
    cities = ['pune', 'mumbai', 'amravati', 'aurangabad', 'nagpur', 'nashik', 'jalgaon', 'kolhapur']
    for city in cities:
        if city in input_name.lower() and city not in scraped_name.lower():
            # If city is strongly specified in input but missing in scraped (and scraped has a different city)
            for other_city in cities:
                if other_city in scraped_name.lower() and other_city != city:
                    confidence -= 30  # Penalize heavily

    return confidence >= 70, confidence
