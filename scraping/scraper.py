import requests
from bs4 import BeautifulSoup
import json
import time
import re
import unicodedata

# --- 1. CONFIGURATION: ALL 7 GENED CATEGORIES ---
BASE_URL = "https://bulletins.psu.edu"

TARGET_URLS = [
    # 1. Quantification (GQ)
    "https://bulletins.psu.edu/undergraduate/general-education/course-lists/quantification/",
    # 2. Arts (GA)
    "https://bulletins.psu.edu/undergraduate/general-education/course-lists/arts/",
    # 3. Humanities (GH)
    "https://bulletins.psu.edu/undergraduate/general-education/course-lists/humanities/",
    # 4. Social & Behavioral Sciences (GS)
    "https://bulletins.psu.edu/undergraduate/general-education/course-lists/social-behavioral-sciences/",
    # 5. Natural Sciences (GN)
    "https://bulletins.psu.edu/undergraduate/general-education/course-lists/natural-sciences/",
    # 6. Health and Wellness (GHW) - ADDED
    "https://bulletins.psu.edu/undergraduate/general-education/course-lists/health-wellness/",
    # 7. Writing/Speaking (GWS) - ADDED
    "https://bulletins.psu.edu/undergraduate/general-education/course-lists/writing-speaking/"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def clean_text(text):
    """
    Normalizes unicode characters (fixes \u00a0 non-breaking spaces) and strips whitespace.
    """
    if not text: return ""
    return unicodedata.normalize("NFKD", text).strip()

def get_course_details(course_url):
    """
    Visits the specific course page to scrape Prerequisites, Attributes, and Inter-Domain flags.
    """
    try:
        response = requests.get(course_url, headers=headers)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text()

        # --- 1. Logic: Extract Prerequisites ---
        prereq_text = "None"
        # Regex to find text after "Enforced Prerequisite at Enrollment:" until a newline
        prereq_match = re.search(r"Enforced Prerequisite at Enrollment:\s*(.*?)(?:\n|$)", text_content)
        if prereq_match:
            prereq_text = clean_text(prereq_match.group(1))

        # --- 2. Logic: GenEd Attributes & Inter-Domain Flag ---
        gen_ed_attrs = []
        is_inter_domain = False
        
        # Check specific codes in the page text
        if "Arts (GA)" in text_content: gen_ed_attrs.append("GA")
        if "Humanities (GH)" in text_content: gen_ed_attrs.append("GH")
        if "Social and Behavioral Sciences (GS)" in text_content: gen_ed_attrs.append("GS")
        if "Natural Sciences (GN)" in text_content: gen_ed_attrs.append("GN")
        if "Quantification (GQ)" in text_content: gen_ed_attrs.append("GQ")
        if "Health and Wellness (GHW)" in text_content: gen_ed_attrs.append("GHW")
        if "Writing/Speaking (GWS)" in text_content: gen_ed_attrs.append("GWS") # Added GWS check
        
        # Logic: If course has >1 domain OR text explicitly says "Inter-Domain"
        if len(gen_ed_attrs) > 1 or "Inter-Domain" in text_content:
            is_inter_domain = True

        # --- 3. Logic: Cultural Attributes (Triple Dip) ---
        cultural_attrs = []
        if "United States Cultures (US)" in text_content: cultural_attrs.append("US")
        if "International Cultures (IL)" in text_content: cultural_attrs.append("IL")

        return {
            "prerequisites_raw": prereq_text,
            "genEdAttributes": list(set(gen_ed_attrs)), # Remove duplicates
            "culturalAttributes": cultural_attrs,
            "interDomain": is_inter_domain
        }

    except Exception as e:
        print(f"Error scraping details for {course_url}: {e}")
        return None

def main():
    master_course_list = []
    # Use a set to track seen course codes to prevent duplicates across lists
    seen_codes = set()

    for url in TARGET_URLS:
        print(f"--- Scraping list: {url} ---")
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the course table rows (sc_courselist table)
            rows = soup.select('table.sc_courselist tbody tr')

            for row in rows:
                # Find the link tag which contains the course code
                link_tag = row.select_one('a.bubblelink')
                if not link_tag:
                    continue

                # Normalize the Course Code
                raw_code = link_tag.get_text(strip=True)
                course_code = clean_text(raw_code)
                
                # Skip if we already scraped this course (e.g., Inter-domain appears in 2 lists)
                if course_code in seen_codes:
                    continue

                # Extract Title and Credits
                try:
                    course_title = clean_text(row.select_one('td:nth-of-type(2)').get_text())
                    credits_text = clean_text(row.select_one('td.hourscol').get_text())
                except:
                    continue # Skip rows that don't match structure
                
                # Generate full URL for details
                detail_url = BASE_URL + link_tag['href']
                
                print(f"Processing: {course_code}...")

                # --- Intelligence Data (Deep Scrape) ---
                details = get_course_details(detail_url)
                
                if details:
                    course_obj = {
                        "courseCode": course_code,
                        "title": course_title,
                        "credits": credits_text,
                        "detailsUrl": detail_url,
                        **details
                    }
                    master_course_list.append(course_obj)
                    seen_codes.add(course_code)
                
                # Sleep to be polite
                time.sleep(0.2)
        except Exception as e:
            print(f"Failed to scrape URL {url}: {e}")

    # Save to JSON
    output_filename = 'gened_courses_golden_record.json'
    with open(output_filename, 'w') as f:
        json.dump(master_course_list, f, indent=2)
    
    print(f"\nSuccess! Scraped {len(master_course_list)} courses. Saved to {output_filename}.")

if __name__ == "__main__":
    main()