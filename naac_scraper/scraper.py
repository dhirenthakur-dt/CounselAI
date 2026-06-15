import os
import requests
import pandas as pd
import logging
from config import NAAC_EXCEL_URL, LOCAL_EXCEL_CACHE
from matcher import is_valid_match

class NAACDataLoader:
    _instance = None
    _df = None

    @classmethod
    def get_data(cls):
        if cls._df is None:
            cls.load_data()
        return cls._df

    @classmethod
    def load_data(cls):
        if not os.path.exists(LOCAL_EXCEL_CACHE):
            logging.info(f"Downloading NAAC Master List from {NAAC_EXCEL_URL}")
            try:
                response = requests.get(NAAC_EXCEL_URL, stream=True)
                response.raise_for_status()
                with open(LOCAL_EXCEL_CACHE, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                logging.info("Downloaded NAAC Master List successfully.")
            except Exception as e:
                logging.error(f"Failed to download NAAC Excel: {e}")
                raise e

        logging.info("Loading NAAC Master List into memory...")
        # NAAC usually puts colleges in sheet index 0 or 1. Let's read all sheets and combine if needed, 
        # or just try reading sheet 1, but we should be robust.
        try:
            # We assume it's an excel with 'HEI Name' column
            df = pd.read_excel(LOCAL_EXCEL_CACHE, sheet_name=None)
            combined = []
            for sheet_name, data in df.items():
                if 'HEI Name' in data.columns:
                    combined.append(data)
            
            if combined:
                cls._df = pd.concat(combined, ignore_index=True)
                # Fill NAs
                cls._df = cls._df.fillna('')
                logging.info(f"Loaded {len(cls._df)} accredited institutions.")
            else:
                logging.error("Could not find 'HEI Name' column in the Excel file.")
                cls._df = pd.DataFrame()
        except Exception as e:
            logging.error(f"Error reading Excel file: {e}")
            cls._df = pd.DataFrame()

def find_best_match(college_code, college_name):
    df = NAACDataLoader.get_data()
    if df.empty:
        return None

    best_match = None
    highest_confidence = 0.0

    # Optimization: If exact match
    # Since iterating 10000 rows can be slow, let's just iterate
    for _, row in df.iterrows():
        hei_name = str(row.get('HEI Name', ''))
        address = str(row.get('Address', ''))
        
        # Pass address as state since it contains state info usually
        is_valid, confidence = is_valid_match(college_name, hei_name, state=address)
        
        if is_valid and confidence > highest_confidence:
            highest_confidence = confidence
            best_match = row
            if confidence >= 95.0:
                break # Exact match found, stop searching

    if best_match is not None:
        return {
            'college_code': college_code,
            'college_name': college_name,
            'matched_college_name': best_match.get('HEI Name', ''),
            'naac_grade': str(best_match.get('Current Grade', '')),
            'cgpa': str(best_match.get('Current CGPA', '')),
            'accreditation_status': 'Accredited',
            'cycle': str(best_match.get('Current Cycle Number', '')),
            'validity': str(best_match.get('Date Of Declaration', '')),
            'search_confidence': highest_confidence,
            'source_url': NAAC_EXCEL_URL
        }

    return {
        'college_code': college_code,
        'college_name': college_name,
        'search_confidence': highest_confidence,
        'source_url': NAAC_EXCEL_URL
    }
