import os
import re
import csv
import time
import psycopg2
from dotenv import load_dotenv
from tavily import TavilyClient

# Load .env from ai-service
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'ai-service', '.env')
load_dotenv(dotenv_path)

TAVILY_KEY = os.getenv("TAVILY_API_KEY")
if not TAVILY_KEY:
    raise ValueError("TAVILY_API_KEY not found in ai-service/.env")

client = TavilyClient(api_key=TAVILY_KEY)

def extract_naac_grade(text):
    text = text.upper()
    # Looking for grade mentions. We check for longer patterns like A++ first
    patterns = [
        r"(?:NAAC|ACCREDITED|GRADE).*?(A\+\+)",
        r"(?:NAAC|ACCREDITED|GRADE).*?(A\+)",
        r"(?:NAAC|ACCREDITED|GRADE).*?(A[^+])",
        r"(?:NAAC|ACCREDITED|GRADE).*?(B\+\+)",
        r"(?:NAAC|ACCREDITED|GRADE).*?(B\+)",
        r"(?:NAAC|ACCREDITED|GRADE).*?(B[^+])",
        r"(?:NAAC|ACCREDITED|GRADE).*?(C)"
    ]
    
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            grade = m.group(1).strip()
            if grade in ['A++', 'A+', 'A', 'B++', 'B+', 'B', 'C']:
                return grade
                
    # Direct fallbacks
    if re.search(r"GRADE:?\s*A\+\+", text, re.IGNORECASE): return "A++"
    if re.search(r"GRADE:?\s*A\+", text, re.IGNORECASE): return "A+"
    if re.search(r"GRADE:?\s*A", text, re.IGNORECASE): return "A"
    
    return None

def run_test():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="counselai_db",
        user="postgres",
        password="123"
    )
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM colleges WHERE naac_grade IS NULL AND is_verified = TRUE ORDER BY name;")
    colleges = cur.fetchall()
    
    print(f"Testing NAAC fetch for {len(colleges)} colleges...")
    
    results = []
    
    # Prepare CSV
    os.makedirs('data/import', exist_ok=True)
    csv_file = open('data/import/naac_results.csv', 'w', newline='', encoding='utf-8')
    writer = csv.writer(csv_file)
    writer.writerow(["college_id", "college_name", "naac_grade", "found"])
    
    for cid, cname in colleges:
        query = f"{cname} NAAC grade accreditation Maharashtra"
        try:
            search_res = client.search(query=query, max_results=3, search_depth="basic")
            all_content = " ".join([r.get("content", "") for r in search_res.get("results", [])])
            
            grade = extract_naac_grade(all_content)
            
            if grade:
                cur.execute("UPDATE colleges SET naac_grade = %s WHERE id = %s", (grade, cid))
                print(f"[OK] {cname[:45]:<45} -> {grade}")
                writer.writerow([cid, cname, grade, "yes"])
                results.append((cname, grade, all_content[:100].replace('\n', ' ')))
            else:
                print(f"[NOT FOUND] {cname[:45]:<45} -> NOT FOUND")
                writer.writerow([cid, cname, "", "no"])
                results.append((cname, "NOT FOUND", ""))
                
        except Exception as e:
            print(f"Error fetching {cname}: {e}")
            writer.writerow([cid, cname, "", f"error: {e}"])
            
        time.sleep(1.5)
        
    csv_file.close()
    cur.close()
    conn.close()
    
    print("\n--- TEST SUMMARY ---")
    print(f"{'College Name':<50} | {'Grade':<10} | {'Snippet'}")
    print("-" * 100)
    for name, grade, snip in results:
        print(f"{name[:48]:<50} | {grade:<10} | {snip[:30]}...")

if __name__ == "__main__":
    run_test()
