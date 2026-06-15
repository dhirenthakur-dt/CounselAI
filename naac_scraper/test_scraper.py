from scraper import find_best_match
import json

res = find_best_match("1001", "Government College of Engineering Amravati")
print(json.dumps(res, indent=4))
