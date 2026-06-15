import os

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

# Ensure directories exist
for directory in [DATA_DIR, LOGS_DIR, OUTPUT_DIR]:
    os.makedirs(directory, exist_ok=True)

# File paths
INPUT_CSV = r"D:\6th Semster\CounselAI\data\import\colleges.csv"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, 'naac_college_data.csv')
OUTPUT_EXCEL = os.path.join(OUTPUT_DIR, 'naac_college_data.xlsx')
OUTPUT_JSON = os.path.join(OUTPUT_DIR, 'naac_college_data.json')
CACHE_DB = os.path.join(DATA_DIR, 'cache.db')

# Logging
LOG_SUCCESS = os.path.join(LOGS_DIR, 'success.log')
LOG_FAILED = os.path.join(LOGS_DIR, 'failed.log')

# Scraper Settings
NAAC_EXCEL_URL = "http://naac.gov.in/images/docs/ACCREDITATION_STATUS/Institutions_accredited_by_NAAC_having_valid_accreditation-as_on_14082025_1.xlsx"
LOCAL_EXCEL_CACHE = os.path.join(DATA_DIR, 'naac_master_list.xlsx')
MAX_WORKERS = 10

# Matching Thresholds
EXACT_MATCH_THRESHOLD = 95
HIGH_CONFIDENCE_THRESHOLD = 85
POSSIBLE_MATCH_THRESHOLD = 70
