import csv
import re
import psycopg2

def normalize(name):
    # lowercase and remove punctuation
    name = name.lower()
    name = re.sub(r'[^\w\s]', '', name)
    return set(name.split())

def run_phase1():
    print("Connecting to DB...")
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="counselai_db",
        user="postgres",
        password="123"
    )
    conn.autocommit = True
    cur = conn.cursor()

    print("Adding is_verified column if not exists...")
    cur.execute("ALTER TABLE colleges ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;")

    print("Fetching existing colleges from DB...")
    cur.execute("SELECT id, name FROM colleges;")
    db_colleges = cur.fetchall()

    csv_colleges = []
    print("Reading CSV...")
    with open('data/colleges.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            csv_colleges.append(row['college_name'])

    matched_count = 0
    unmatched_count = 0
    matched_samples = []

    # Reset for idempotency
    cur.execute("UPDATE colleges SET is_verified = FALSE;")

    print("Starting fuzzy matching...")
    for csv_name in csv_colleges:
        csv_words = normalize(csv_name)
        if not csv_words:
            continue
            
        best_match_id = None
        best_score = 0
        best_db_name = None
        
        for db_id, db_name in db_colleges:
            db_words = normalize(db_name)
            if not db_words: continue
            
            # Calculate word overlap percentage based on CSV words
            intersection = csv_words.intersection(db_words)
            score = len(intersection) / len(csv_words)
            
            if score > best_score:
                best_score = score
                best_match_id = db_id
                best_db_name = db_name
                
        if best_score >= 0.70:
            # Match found!
            cur.execute("UPDATE colleges SET is_verified = TRUE WHERE id = %s", (best_match_id,))
            matched_count += 1
            if len(matched_samples) < 5:
                matched_samples.append((csv_name, best_db_name, best_score))
        else:
            unmatched_count += 1

    cur.execute("SELECT COUNT(*) FROM colleges WHERE is_verified = TRUE;")
    verified_count = cur.fetchone()[0]

    print("-" * 50)
    print(f"Total CSV Colleges Read: {len(csv_colleges)}")
    print(f"Matched Colleges: {matched_count}")
    print(f"Unmatched CSV Colleges: {unmatched_count}")
    print(f"Total Verified DB Colleges: {verified_count}")
    print("-" * 50)
    print("Sample Matches:")
    for c, d, s in matched_samples:
        print(f"  CSV: {c[:45]:<45} -> DB: {d[:45]:<45} (Score: {s:.2f})")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    run_phase1()
