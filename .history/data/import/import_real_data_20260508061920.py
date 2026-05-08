"""
CounselAI — Real Data Import Script
=====================================
Imports 157,206 real DTE cutoff records into PostgreSQL.

Run this script from the folder where cutoffs.csv is located.

Steps it performs:
1. Clears existing test data
2. Imports 692 real colleges
3. Imports 3,980 real branches
4. Imports 157,206 real cutoff records
5. Shows final statistics

Usage:
  python import_real_data.py

Requirements:
  pip install psycopg2-binary
"""

import psycopg2
import psycopg2.extras
import csv
import os
import time

# ─── CONFIG — Change password if yours is different ───────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "database": "counselai_db",
    "user":     "postgres",
    "password": "123"
}

# Path to your cutoffs.csv file
CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cutoffs.csv")

# ─── CONNECT ──────────────────────────────────────────────────────
def get_conn():
    return psycopg2.connect(**DB_CONFIG)

# ─── STEP 1: CLEAR EXISTING TEST DATA ────────────────────────────
def clear_test_data(conn):
    print("\n🗑️  Step 1: Clearing existing test data...")
    cur = conn.cursor()

    cur.execute("DELETE FROM cutoffs")
    cur.execute("DELETE FROM branches")
    cur.execute("DELETE FROM colleges")

    conn.commit()
    cur.close()
    print("   ✅ Test data cleared")

# ─── STEP 2: IMPORT COLLEGES ──────────────────────────────────────
def import_colleges(conn, rows):
    print("\n🏫 Step 2: Importing colleges...")

    # Build unique colleges dict
    colleges = {}
    for r in rows:
        code = r["college_code"].strip()
        name = r["college_name"].strip()
        if code and name and code not in colleges:
            colleges[code] = name

    cur = conn.cursor()

    # Detect district from college name keywords
    district_keywords = {
        "Pune": "Pune", "Nashik": "Nashik", "Mumbai": "Mumbai",
        "Nagpur": "Nagpur", "Aurangabad": "Aurangabad", "Amravati": "Amravati",
        "Kolhapur": "Kolhapur", "Sangli": "Sangli", "Solapur": "Solapur",
        "Nanded": "Nanded", "Latur": "Latur", "Jalgaon": "Jalgaon",
        "Akola": "Akola", "Yavatmal": "Yavatmal", "Buldhana": "Buldhana",
        "Washim": "Washim", "Wardha": "Wardha", "Bhandara": "Bhandara",
        "Gondia": "Gondia", "Chandrapur": "Chandrapur", "Gadchiroli": "Gadchiroli",
        "Nandurbar": "Nandurbar", "Dhule": "Dhule", "Ahmednagar": "Ahmednagar",
        "Beed": "Beed", "Osmanabad": "Osmanabad", "Parbhani": "Parbhani",
        "Hingoli": "Hingoli", "Ratnagiri": "Ratnagiri", "Sindhudurg": "Sindhudurg",
        "Raigad": "Raigad", "Thane": "Thane", "Palghar": "Palghar",
        "Satara": "Satara", "Sholapur": "Solapur", "Shegaon": "Buldhana",
        "Navi Mumbai": "Mumbai", "Kalyan": "Thane", "Vasai": "Palghar",
        "Pimpri": "Pune", "Chinchwad": "Pune", "Hadapsar": "Pune",
        "Konkan": "Ratnagiri", "Chhatrapati": "Aurangabad", "Sambhajinagar": "Aurangabad",
        "Jalna": "Jalna", "Baramati": "Pune", "Wani": "Yavatmal",
    }

    def detect_district(name):
        for keyword, district in district_keywords.items():
            if keyword.lower() in name.lower():
                return district
        return None

    def detect_type(name):
        name_lower = name.lower()
        if "government" in name_lower or "govt" in name_lower:
            return "Government"
        if "university" in name_lower:
            return "University Department"
        return "Private"

    batch = []
    for code, name in colleges.items():
        district = detect_district(name)
        ctype    = detect_type(name)
        batch.append((name, district, None, ctype, code))

    # Insert all colleges
    cur.executemany("""
        INSERT INTO colleges
        (name, district, city, college_type, website)
        VALUES (%s, %s, %s, %s, %s)
    """, batch)

    conn.commit()
    cur.close()
    print(f"   ✅ {len(colleges):,} colleges imported")
    return len(colleges)


# ─── STEP 3: IMPORT BRANCHES ──────────────────────────────────────
def import_branches(conn, rows):
    print("\n🌿 Step 3: Importing branches...")

    cur = conn.cursor()

    # Build college name → id map
    cur.execute("SELECT id, name, website FROM colleges")
    college_map = {}
    for cid, cname, ccode in cur.fetchall():
        college_map[cname] = cid
        if ccode:
            college_map[ccode] = cid  # also map by code

    # Build unique branches
    branches = {}
    for r in rows:
        college_name = r["college_name"].strip()
        branch_name  = r["branch_name"].strip()
        college_code = r["college_code"].strip()

        college_id = college_map.get(college_name)
        if not college_id:
            college_id = college_map.get(college_code)
        if not college_id:
            continue

        key = (college_id, branch_name)
        if key not in branches:
            # Detect branch code
            branch_code = detect_branch_code(branch_name)
            branches[key] = (college_id, branch_name, branch_code)

    batch = list(branches.values())

    # Insert in chunks
    CHUNK = 500
    for i in range(0, len(batch), CHUNK):
        chunk = batch[i:i+CHUNK]
        cur.executemany("""
            INSERT INTO branches (college_id, branch_name, branch_code)
            VALUES (%s, %s, %s)
        """, chunk)
        conn.commit()

    cur.close()
    print(f"   ✅ {len(branches):,} branches imported")
    return len(branches)


def detect_branch_code(name):
    name_lower = name.lower()
    if "computer science" in name_lower or "computer engineering" in name_lower:
        return "CS"
    if "information technology" in name_lower:
        return "IT"
    if "artificial intelligence" in name_lower or "machine learning" in name_lower:
        return "AIML"
    if "electronics" in name_lower and "telecommunication" in name_lower:
        return "EXTC"
    if "electronics" in name_lower:
        return "ELEX"
    if "mechanical" in name_lower:
        return "MECH"
    if "civil" in name_lower:
        return "CIVIL"
    if "electrical" in name_lower:
        return "ELEC"
    if "chemical" in name_lower:
        return "CHEM"
    if "data science" in name_lower:
        return "DS"
    if "cyber" in name_lower:
        return "CS"
    if "robotics" in name_lower:
        return "ROBOTICS"
    if "instrumentation" in name_lower:
        return "INST"
    if "production" in name_lower:
        return "PROD"
    if "textile" in name_lower:
        return "TEXT"
    if "food" in name_lower:
        return "FOOD"
    if "petroleum" in name_lower:
        return "PET"
    return None


# ─── STEP 4: IMPORT CUTOFFS ───────────────────────────────────────
def import_cutoffs(conn, rows):
    print("\n📊 Step 4: Importing 157,206 cutoff records...")
    print("   This will take 3-5 minutes. Please wait...\n")

    cur = conn.cursor()

    # Build lookup maps
    cur.execute("SELECT id, name, website FROM colleges")
    college_map = {}
    for cid, cname, ccode in cur.fetchall():
        college_map[cname.strip()] = cid
        if ccode:
            college_map[ccode.strip()] = cid

    cur.execute("SELECT id, college_id, branch_name FROM branches")
    branch_map = {}
    for bid, cid, bname in cur.fetchall():
        branch_map[(cid, bname.strip())] = bid

    inserted = 0
    skipped  = 0
    batch    = []
    BATCH    = 1000
    start    = time.time()

    for i, r in enumerate(rows):

        # Progress every 10k rows
        if i > 0 and i % 10000 == 0:
            elapsed = time.time() - start
            pct = (i / len(rows)) * 100
            print(f"   Progress: {i:,}/{len(rows):,} ({pct:.0f}%) — {elapsed:.0f}s elapsed")

        college_name = r["college_name"].strip()
        college_code = r["college_code"].strip()
        branch_name  = r["branch_name"].strip()
        category     = r["category"].strip()

        try:
            year      = int(r["year"])
            cap_round = int(r["cap_round"])
            closing   = float(r["closing_percentile"])
        except (ValueError, KeyError):
            skipped += 1
            continue

        # Validate percentile range
        if not (0.0 <= closing <= 100.0):
            skipped += 1
            continue

        college_id = college_map.get(college_name) or college_map.get(college_code)
        if not college_id:
            skipped += 1
            continue

        branch_id = branch_map.get((college_id, branch_name))

        batch.append((
            college_id, branch_id,
            year, cap_round,
            category, closing
        ))

        if len(batch) >= BATCH:
            try:
                psycopg2.extras.execute_values(cur, """
                    INSERT INTO cutoffs
                    (college_id, branch_id, year, cap_round,
                     category, closing_percentile)
                    VALUES %s
                    ON CONFLICT DO NOTHING
                """, batch)
                inserted += len(batch)
                conn.commit()
                batch = []
            except Exception as e:
                print(f"   ⚠️  Batch error: {e}")
                conn.rollback()
                skipped += len(batch)
                batch = []

    # Final batch
    if batch:
        try:
            psycopg2.extras.execute_values(cur, """
                INSERT INTO cutoffs
                (college_id, branch_id, year, cap_round,
                 category, closing_percentile)
                VALUES %s
                ON CONFLICT DO NOTHING
            """, batch)
            inserted += len(batch)
            conn.commit()
        except Exception as e:
            print(f"   ⚠️  Final batch error: {e}")
            skipped += len(batch)

    cur.close()
    elapsed = time.time() - start
    print(f"\n   ✅ {inserted:,} records inserted")
    print(f"   ⚠️  {skipped:,} records skipped")
    print(f"   ⏱️  Time taken: {elapsed:.0f} seconds")
    return inserted


# ─── STEP 5: SHOW FINAL STATS ─────────────────────────────────────
def show_stats(conn):
    cur = conn.cursor()
    print("\n📊 Final Database Statistics:")
    print("   " + "─"*40)

    for table in ["colleges", "branches", "cutoffs", "documents_required"]:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"   {table:<25} {count:>10,} rows")

    print()

    cur.execute("""
        SELECT year, cap_round, COUNT(*) as cnt
        FROM cutoffs
        GROUP BY year, cap_round
        ORDER BY year, cap_round
    """)
    print("   Cutoffs by year and round:")
    for row in cur.fetchall():
        print(f"     {row[0]} Round {row[1]}: {row[2]:,} records")

    print()
    cur.execute("""
        SELECT category, COUNT(*) as cnt
        FROM cutoffs
        GROUP BY category
        ORDER BY cnt DESC
        LIMIT 10
    """)
    print("   Top 10 categories:")
    for row in cur.fetchall():
        print(f"     {row[0]:<15} {row[1]:>8,}")

    print()
    cur.execute("""
        SELECT c.name, COUNT(cu.id) as cnt
        FROM colleges c
        JOIN cutoffs cu ON cu.college_id = c.id
        GROUP BY c.name
        ORDER BY cnt DESC
        LIMIT 5
    """)
    print("   Top 5 colleges by cutoff records:")
    for row in cur.fetchall():
        print(f"     {row[0][:50]:<50} {row[1]:>6,}")

    cur.close()


# ─── MAIN ─────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  CounselAI — Real Data Import")
    print("  Importing 157,206 DTE Maharashtra Records")
    print("=" * 60)

    # Check CSV exists
    if not os.path.exists(CSV_PATH):
        print(f"\n❌ cutoffs.csv not found at: {CSV_PATH}")
        print("   Put cutoffs.csv in same folder as this script")
        return

    # Load CSV
    print(f"\n📂 Loading {CSV_PATH}...")
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    print(f"   ✅ Loaded {len(rows):,} rows")

    # Connect
    print("\n🔌 Connecting to PostgreSQL...")
    try:
        conn = get_conn()
        print("   ✅ Connected to counselai_db")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        print(f"   Check password in DB_CONFIG at top of script")
        return

    total_start = time.time()

    # Run all steps
    clear_test_data(conn)
    import_colleges(conn, rows)
    import_branches(conn, rows)
    import_cutoffs(conn, rows)
    show_stats(conn)

    conn.close()

    total_time = time.time() - total_start
    print(f"\n{'='*60}")
    print(f"  ✅ Import Complete in {total_time:.0f} seconds")
    print(f"  Restart your Spring Boot backend now.")
    print(f"  Your system now has real DTE Maharashtra data!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()