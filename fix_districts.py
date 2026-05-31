import psycopg2
import os
import requests
import json

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

conn = psycopg2.connect(
    dbname="counselai_db",
    user="postgres",
    password="123",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

cursor.execute("SELECT id, name FROM colleges WHERE district IS NULL OR district = '';")
colleges = cursor.fetchall()

print(f"Found {len(colleges)} colleges missing district.")

if len(colleges) == 0:
    exit(0)

# Batch process with Groq
prompt = """
I have a list of Engineering colleges in Maharashtra. Their names usually contain their city, town, or district.
For each college, identify the exact District in Maharashtra it belongs to (e.g., Pune, Mumbai, Nagpur, Dhule, Nandurbar, Jalgaon, Nashik, Ahmednagar, Satara, Sangli, Kolhapur, Solapur, Aurangabad, Jalna, Beed, Nanded, Latur, Parbhani, Hingoli, Osmanabad, Amravati, Akola, Washim, Buldhana, Yavatmal, Wardha, Bhandara, Gondia, Chandrapur, Gadchiroli, Thane, Palghar, Raigad, Ratnagiri, Sindhudurg).

Only output a JSON object where the key is the ID and the value is the District name (just the name, e.g. "Dhule").
Do not output anything other than the JSON object.

Colleges:
"""

for c in colleges:
    prompt += f"ID: {c[0]}, Name: {c[1]}\n"

headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "llama-3.3-70b-versatile",
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.1,
    "response_format": {"type": "json_object"}
}

print("Asking Groq...")
response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
result = response.json()

try:
    district_map = json.loads(result['choices'][0]['message']['content'])
    print(f"Mapped {len(district_map)} districts. Updating DB...")
    
    updated_count = 0
    for cid, dist in district_map.items():
        if dist and dist.strip():
            cursor.execute("UPDATE colleges SET district = %s WHERE id = %s", (dist.strip(), int(cid)))
            updated_count += 1
            
    conn.commit()
    print(f"Successfully updated {updated_count} colleges!")
except Exception as e:
    print("Error parsing or updating:", e)
    print(result)

cursor.close()
conn.close()
