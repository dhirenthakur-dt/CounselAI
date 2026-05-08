"""
CounselAI — Fixed Import Script
=================================
Fixes the unique constraint to include branch_id
then reimports all 157,206 records correctly.

Run from same folder as cutoffs.csv
"""

import psycopg2
import psycopg2.extras
import csv
import os
import time

DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "database": "counselai_db",
    "user":     "postgres",
    "password": "counselai123"   # ← change if needed
}

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cutoffs.csv")


def get_conn():
    return psycopg2.connect(**DB_CONFIG)


def fix_constraint(conn):
    """Drop wrong constraint and add correct one."""
    print("\n🔧 Step 1: Fixing unique constraint...")
    cur = conn.cursor()

    # Drop old wrong constraint
    cur.execute("""
        ALTER TABLE cutoffs
        DROP CONSTRAINT IF EXISTS unique_cutoff
    """)

    # Clear all cutoffs for clean import
    cur.execute("DELETE FROM cutoffs")
    cur.execute("DELETE FROM branches")
    cur.execute("DELETE FROM colleges")

    conn.commit()
    cur.close()
    print("   ✅ Old constraint removed, tables cleared")


def detect_branch_code(name):
    n = name.lower()
    if "computer science" in n or "computer engineering" in n: return "CS"
    if "information technology" in n: return "IT"
    if "artificial intelligence" in n or "machine learning" in n: return "AIML"
    if "data science" in n: return "DS"
    if "electronics" in n and "telecommunication" in n: return "EXTC"
    if "electronics" in n: return "ELEX"
    if "mechanical" in n: return "MECH"
    if "civil" in n: return "CIVIL"
    if "electrical" in n: return "ELEC"
    if "chemical" in n: return "CHEM"
    if "cyber" in n: return "CS"
    if "robotics" in n: return "ROBOTICS"
    if "instrumentation" in n: return "INST"
    if "production" in n: return "PROD"
    if "food" in n: return "FOOD"
    if "textile" in n: return "TEXT"
    return None


def detect_district(name):
    keywords = {
        "Pune": "Pune", "Nashik": "Nashik", "Mumbai": "Mumbai",
        "Nagpur": "Nagpur", "Aurangabad": "Aurangabad", "Amravati": "Amravati",
        "Kolhapur": "Kolhapur", "Sangli": "Sangli", "Solapur": "Solapur",
        "Nanded": "Nanded", "Latur": "Latur", "Jalgaon": "Jalgaon",
        "Akola": "Akola", "Yavatmal": "Yavatmal", "Buldhana": "Buldhana",
        "Wardha": "Wardha", "Chandrapur": "Chandrapur",
        "Nandurbar": "Nandurbar", "Dhule": "Dhule",
        "Ahmednagar": "Ahmednagar", "Beed": "Beed",
        "Osmanabad": "Osmanabad", "Parbhani": "Parbhani",
        "Ratnagiri": "Ratnagiri", "Thane": "Thane", "Palghar": "Palghar",
        "Satara": "Satara", "Shegaon": "Buldhana",
        "Navi Mumbai": "Mumbai", "Kalyan": "Thane",
        "Pimpri": "Pune", "Chinchwad": "Pune", "Baramati": "Pune",
        "Sambhajinagar": "Aurangabad", "Jalna": "Jalna",
        "Wani": "Yavatmal", "Gondia": "Gondia", "Bhandara": "Bhandara",
        "Washim": "Washim", "Gadchiroli": "Gadchiroli",
    }
    for keyword, district in keywords.items():
        if keyword.lower() in name.lower():
            return district
    return None


def detect_type(name):
    n = name.lower()
    if "government" in n or "govt" in n: return "Government"
    if "university" in n: return "University Department"
    return "Private"


def import_colleges(conn, rows):
    print("\n🏫 Step 2: Importing colleges...")
    colleges = {}
    for r in rows:
        code = r["college_code"].strip()
        name = r["college_name"].strip()
        if code and name and code not in colleges:
            colleges[code] = name

    cur = conn.cursor()
    batch = []
    for code, name in colleges.items():
        batch.append((name, detect_district(name), None, detect_type(name), code))

    cur.executemany("""
        INSERT INTO colleges (name, district, city, college_type, website)
        VALUES (%s, %s, %s, %s, %s)
    """, batch)
    conn.commit()
    cur.close()
    print(f"   ✅ {len(colleges):,} colleges imported")


def import_branches(conn, rows):
    print("\n🌿 Step 3: Importing branches...")
    cur = conn.cursor()

    cur.execute("SELECT id, name, website FROM colleges")
    college_map = {}
    for cid, cname, ccode in cur.fetchall():
        college_map[cname.strip()] = cid
        if ccode:
            college_map[ccode.strip()] = cid

    branches = {}
    for r in rows:
        cname  = r["college_name"].strip()
        bname  = r["branch_name"].strip()
        ccode  = r["college_code"].strip()
        cid    = college_map.get(cname) or college_map.get(ccode)
        if not cid:
            continue
        key = (cid, bname)
        if key not in branches:
            branches[key] = (cid, bname, detect_branch_code(bname))

    batch = list(branches.values())
    CHUNK = 500
    for i in range(0, len(batch), CHUNK):
        cur.executemany("""
            INSERT INTO branches (college_id, branch_name, branch_code)
            VALUES (%s, %s, %s)
        """, batch[i:i+CHUNK])
        conn.commit()

    cur.close()
    print(f"   ✅ {len(branches):,} branches imported")


def import_cutoffs(conn, rows):
    print("\n📊 Step 4: Importing cutoff records...")
    print("   Please wait...\n")

    cur = conn.cursor()

    # Build maps
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
        if i > 0 and i % 20000 == 0:
            elapsed = time.time() - start
            pct = (i / len(rows)) * 100
            print(f"   Progress: {i:,}/{len(rows):,} ({pct:.0f}%) — {elapsed:.0f}s")

        try:
            year      = int(r["year"])
            cap_round = int(r["cap_round"])
            closing   = float(r["closing_percentile"])
        except (ValueError, KeyError):
            skipped += 1
            continue

        if not (0.0 <= closing <= 100.0):
            skipped += 1
            continue

        cname = r["college_name"].strip()
        ccode = r["college_code"].strip()
        bname = r["branch_name"].strip()
        cat   = r["category"].strip()

        cid = college_map.get(cname) or college_map.get(ccode)
        if not cid:
            skipped += 1
            continue

        bid = branch_map.get((cid, bname))

        batch.append((cid, bid, year, cap_round, cat, closing))

        if len(batch) >= BATCH:
            try:
                psycopg2.extras.execute_values(cur, """
                    INSERT INTO cutoffs
                    (college_id, branch_id, year, cap_round,
                     category, closing_percentile)
                    VALUES %s
                """, batch)
                inserted += len(batch)
                conn.commit()
                batch = []
            except Exception as e:
                print(f"   ⚠️  Batch error: {e}")
                conn.rollback()
                skipped += len(batch)
                batch = []

    if batch:
        try:
            psycopg2.extras.execute_values(cur, """
                INSERT INTO cutoffs
                (college_id, branch_id, year, cap_round,
                 category, closing_percentile)
                VALUES %s
            """, batch)
            inserted += len(batch)
            conn.commit()
        except Exception as e:
            print(f"   ⚠️  Final batch error: {e}")
            skipped += len(batch)

    elapsed = time.time() - start
    cur.close()
    print(f"\n   ✅ {inserted:,} records inserted")
    print(f"   ⚠️  {skipped:,} records skipped")
    print(f"   ⏱️  Time: {elapsed:.0f} seconds")
    return inserted


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
        SELECT year, cap_round, COUNT(*)
        FROM cutoffs GROUP BY year, cap_round
        ORDER BY year, cap_round
    """)
    print("   Records by year and round:")
    for row in cur.fetchall():
        print(f"     {row[0]} Round {row[1]}: {row[2]:,}")

    print()
    cur.execute("""
        SELECT category, COUNT(*) as cnt
        FROM cutoffs GROUP BY category
        ORDER BY cnt DESC LIMIT 8
    """)
    print("   Top 8 categories:")
    for row in cur.fetchall():
        print(f"     {row[0]:<15} {row[1]:>8,}")

    cur.close()


def main():
    print("=" * 60)
    print("  CounselAI — Fixed Real Data Import")
    print("  Target: 157,206 DTE Maharashtra Records")
    print("=" * 60)

    if not os.path.exists(CSV_PATH):
        print(f"\n❌ cutoffs.csv not found at: {CSV_PATH}")
        return

    print(f"\n📂 Loading CSV...")
    with open(CSV_PATH, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"   ✅ Loaded {len(rows):,} rows")

    print("\n🔌 Connecting to PostgreSQL...")
    try:
        conn = get_conn()
        print("   ✅ Connected")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return

    total_start = time.time()

    fix_constraint(conn)
    import_colleges(conn, rows)
    import_branches(conn, rows)
    import_cutoffs(conn, rows)
    show_stats(conn)

    conn.close()
    total = time.time() - total_start

    print(f"\n{'='*60}")
    print(f"  ✅ Import Complete in {total:.0f} seconds")
    print(f"  Now restart Spring Boot backend!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()