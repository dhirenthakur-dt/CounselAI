from bs4 import BeautifulSoup
import re
import logging

def clean_text(text):
    if not text:
        return ""
    return text.replace('\n', ' ').replace('\r', '').strip()

def validate_grade(grade):
    allowed_grades = ['A++', 'A+', 'A', 'B++', 'B+', 'B', 'C', 'Accredited', 'Not Accredited']
    if grade in allowed_grades:
        return grade
    
    # Try to extract grade if embedded in string
    for allowed in allowed_grades:
        if allowed in grade.split():
            return allowed
            
    return "Invalid/Unknown"

def extract_accreditation_details(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Assuming NAAC results are displayed in a table.
    # We will try to find a table and parse rows.
    # Returns a list of dictionaries.
    results = []
    
    tables = soup.find_all('table')
    for table in tables:
        headers = []
        for th in table.find_all('th'):
            headers.append(clean_text(th.get_text()).lower())
            
        if not headers:
            # Maybe headers are in first row td
            first_row = table.find('tr')
            if first_row:
                for td in first_row.find_all(['td', 'th']):
                    headers.append(clean_text(td.get_text()).lower())
        
        # Mapping header keywords to our keys
        header_map = {}
        for idx, h in enumerate(headers):
            if 'name' in h or 'institution' in h:
                header_map['institution_name'] = idx
            elif 'cgpa' in h:
                header_map['cgpa'] = idx
            elif 'grade' in h:
                header_map['grade'] = idx
            elif 'cycle' in h:
                header_map['cycle'] = idx
            elif 'valid' in h or 'upto' in h:
                header_map['validity'] = idx
            elif 'state' in h:
                header_map['state'] = idx
            elif 'status' in h:
                header_map['status'] = idx

        if 'institution_name' not in header_map:
            continue # Not the right table
            
        rows = table.find_all('tr')
        for row in rows[1:]: # Skip header
            cols = row.find_all('td')
            if len(cols) < len(header_map):
                continue
                
            data = {}
            for key, idx in header_map.items():
                if idx < len(cols):
                    data[key] = clean_text(cols[idx].get_text())
            
            # Format and validate
            if 'grade' in data:
                data['grade'] = validate_grade(data['grade'])
            
            # If status not explicitly present, derive it
            if 'status' not in data:
                if data.get('grade') and data.get('grade') != 'Invalid/Unknown':
                    data['status'] = 'Accredited'
                else:
                    data['status'] = 'Unknown'
                    
            if 'institution_name' in data and data['institution_name']:
                results.append(data)
                
    return results
