from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_college_live(college_name: str) -> dict:
    """
    Finds official direct links for college info.
    Instead of extracting data (unreliable),
    returns direct URLs to official pages.
    """
    
    result = {
        "college_name":      college_name,
        "fee_link":          None,
        "hostel_link":       None, 
        "placement_link":    None,
        "admission_link":    None,
        "official_website":  None,
        "naac_link":         None,
        "quick_facts":       [],
        "error":             None
    }
    
    try:
        # Search 1: Official website + fee
        fee_results = client.search(
            query=f"{college_name} official website fee structure admission 2024-25",
            max_results=5,
            search_depth="basic"
        )
        
        # Search 2: Placement
        placement_results = client.search(
            query=f"{college_name} placement 2024 average package official",
            max_results=3,
            search_depth="basic"
        )
        
        # Search 3: Hostel
        hostel_results = client.search(
            query=f"{college_name} hostel facility accommodation students",
            max_results=3,
            search_depth="basic"
        )
        
        # Process fee/official results
        for r in fee_results.get("results", []):
            url   = r.get("url", "").lower()
            title = r.get("title", "").lower()
            content = r.get("content", "").lower()
            raw_url = r.get("url", "")
            
            # Find official website (prefer .ac.in or .edu)
            if not result["official_website"]:
                if any(x in url for x in [".ac.in", ".edu.in", "official"]):
                    result["official_website"] = raw_url
                    
            # Find fee page
            if not result["fee_link"]:
                if any(x in url+title for x in ["fee", "fees", "admission", "tuition"]):
                    result["fee_link"] = raw_url
                    
            # Quick facts from content (small snippets, not full extraction)
            if "naac" in content and not result["naac_link"]:
                # Extract just the grade mention for quick fact
                import re
                m = re.search(r"naac[^\w]*(?:grade|accredited|rating)?[^\w]*([abcABC][+]{0,2})", content)
                if m:
                    grade = m.group(1).upper()
                    if grade in ["A++","A+","A","B++","B+","B","C"]:
                        result["quick_facts"].append(f"NAAC Grade: {grade}")
            
            if "placement" in content:
                import re
                m = re.search(r"([\d.]+)\s*(?:lpa|lakh|lakhs)\s*(?:average|avg|package|salary)", content, re.IGNORECASE)
                if m:
                    result["quick_facts"].append(f"Avg Package: {m.group(0)[:40]}")
                    
        # Process placement results
        for r in placement_results.get("results", []):
            url = r.get("url", "").lower()
            raw_url = r.get("url", "")
            if not result["placement_link"]:
                if any(x in url for x in ["placement", "career", "recruit"]):
                    result["placement_link"] = raw_url
                    
        # Process hostel results    
        for r in hostel_results.get("results", []):
            url = r.get("url", "").lower()
            content = r.get("content", "").lower()
            raw_url = r.get("url", "")
            if not result["hostel_link"]:
                if any(x in url+content for x in ["hostel", "accommodation", "residential"]):
                    result["hostel_link"] = raw_url
                    
            # Quick fact about hostel availability
            if not any("hostel" in f.lower() for f in result["quick_facts"]):
                if "hostel available" in content or "hostel facility" in content:
                    result["quick_facts"].append("Hostel: Available")
                elif "no hostel" in content:
                    result["quick_facts"].append("Hostel: Not Available")
        
        # Fallback: if no official website found, use first result
        if not result["official_website"] and fee_results.get("results"):
            result["official_website"] = fee_results["results"][0].get("url")
            
        print(f"Live search done for {college_name[:40]}")
        print(f"  Official: {result['official_website']}")
        print(f"  Fee link: {result['fee_link']}")
        print(f"  Quick facts: {result['quick_facts']}")
        
    except Exception as e:
        print(f"Live search error: {e}")
        result["error"] = str(e)
    
    return result
