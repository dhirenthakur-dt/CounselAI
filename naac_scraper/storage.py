import sqlite3
import pandas as pd
import json
import logging
from config import CACHE_DB, OUTPUT_CSV, OUTPUT_EXCEL, OUTPUT_JSON

def init_db():
    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS naac_cache (
            college_code TEXT PRIMARY KEY,
            college_name TEXT,
            matched_college_name TEXT,
            naac_grade TEXT,
            cgpa TEXT,
            accreditation_status TEXT,
            cycle TEXT,
            validity TEXT,
            search_confidence REAL,
            source_url TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_cached_result(college_code):
    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM naac_cache WHERE college_code=?', (str(college_code),))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'college_code': row[0],
            'college_name': row[1],
            'matched_college_name': row[2],
            'naac_grade': row[3],
            'cgpa': row[4],
            'accreditation_status': row[5],
            'cycle': row[6],
            'validity': row[7],
            'search_confidence': row[8],
            'source_url': row[9]
        }
    return None

def save_to_cache(result):
    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO naac_cache 
        (college_code, college_name, matched_college_name, naac_grade, cgpa, accreditation_status, cycle, validity, search_confidence, source_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        str(result['college_code']), result['college_name'], result.get('matched_college_name', ''),
        result.get('naac_grade', ''), result.get('cgpa', ''), result.get('accreditation_status', ''),
        result.get('cycle', ''), result.get('validity', ''), result.get('search_confidence', 0.0),
        result.get('source_url', '')
    ))
    conn.commit()
    conn.close()

def export_results():
    conn = sqlite3.connect(CACHE_DB)
    df = pd.read_sql_query("SELECT * FROM naac_cache", conn)
    conn.close()
    
    if df.empty:
        logging.warning("No data to export.")
        return

    # Export to CSV
    df.to_csv(OUTPUT_CSV, index=False)
    # Export to Excel
    df.to_excel(OUTPUT_EXCEL, index=False)
    # Export to JSON
    df.to_json(OUTPUT_JSON, orient='records', indent=4)
    
    logging.info(f"Exported {len(df)} records to CSV, Excel, and JSON.")
