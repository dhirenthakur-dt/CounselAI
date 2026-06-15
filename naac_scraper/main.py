import pandas as pd
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from config import INPUT_CSV, MAX_WORKERS, LOG_SUCCESS, LOG_FAILED
from storage import init_db, get_cached_result, save_to_cache, export_results
from scraper import find_best_match

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_SUCCESS),
        logging.StreamHandler()
    ]
)
error_logger = logging.getLogger('error')
error_logger.addHandler(logging.FileHandler(LOG_FAILED))

def process_college(row):
    college_code = row['college_code']
    college_name = row['college_name']
    
    # Check cache
    cached = get_cached_result(college_code)
    if cached:
        return cached

    # Scrape and match
    try:
        result = find_best_match(college_code, college_name)
        if result:
            save_to_cache(result)
            return result
    except Exception as e:
        error_logger.error(f"Failed to process {college_code} - {college_name}: {str(e)}")
        
    return {
        'college_code': college_code,
        'college_name': college_name,
        'search_confidence': 0.0
    }

def main():
    logging.info("Starting NAAC Automation System")
    init_db()
    
    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        logging.error(f"Input file not found at {INPUT_CSV}")
        return
        
    records = df.to_dict('records')
    total = len(records)
    
    logging.info(f"Loaded {total} colleges from CSV.")
    
    results = []
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_college = {executor.submit(process_college, record): record for record in records}
        
        for future in tqdm(as_completed(future_to_college), total=total, desc="Processing Colleges"):
            try:
                res = future.result()
                results.append(res)
            except Exception as exc:
                record = future_to_college[future]
                error_logger.error(f"College {record['college_code']} generated an exception: {exc}")
                
    logging.info("Processing complete. Exporting results...")
    export_results()
    logging.info("Automation finished.")

if __name__ == "__main__":
    main()
