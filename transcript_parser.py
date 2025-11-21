import re
from pypdf import PdfReader

def parse_transcript_pdf(pdf_path):
    """
    Parses a Penn State transcript PDF to extract completed course codes.
    Logic: Looks for lines containing Course + Number + Grade + Credits.
    """
    completed_courses = []
    
    try:
        reader = PdfReader(pdf_path)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
            
        # Regex to match PSU Transcript lines.
        # Pattern looks for:
        # 1. Course Dept (e.g. CMPSC)
        # 2. Number (e.g. 131)
        # 3. Description (Variable length)
        # 4. Attempted (Float)
        # 5. Earned (Float)
        # 6. Grade (Letters)
        
        # Example line from your data: "CMPSC 131 PROG & COMP I 3.000 3.000 C 6.000"
        # We will use a robust regex that looks for the Subject and Number, 
        # followed eventually by a Grade that isn't F, LD, or W.
        
        lines = full_text.split('\n')
        
        for line in lines:
            # Normalize line
            clean_line = line.strip()
            
            # Look for pattern: "DEPT NUM ... GRADE"
            # e.g. "MATH 140 ... 4.000 ... B"
            
            # 1. Extract Course Code (e.g. "MATH 140")
            code_match = re.search(r'^([A-Z]+)\s+(\d+[A-Z]?)', clean_line)
            if not code_match:
                continue
                
            dept = code_match.group(1)
            num = code_match.group(2)
            full_code = f"{dept} {num}"
            
            # 2. Check for Valid Grade
            # We look for typical passing grades at the end or middle of line
            # Grades: A, A-, B+, B, B-, C+, C, D, P, TR (Transfer)
            # Exclude: F, W, LD (Late Drop), DF (Deferred)
            
            # Simple check: if line contains a passing grade surrounded by spaces or numbers
            has_grade = re.search(r'\s(A|A-|B\+|B|B-|C\+|C|D|P|TR)\s', clean_line)
            
            # Check if "Earned" credits > 0 (Usually appears as X.000)
            # We look for a non-zero number like "3.000" or "4.00"
            earned_credits = re.search(r'\s([0-9]+\.[0-9]+)\s', clean_line)
            is_earned = False
            if earned_credits:
                try:
                    if float(earned_credits.group(1)) > 0.0:
                        is_earned = True
                except:
                    pass

            if has_grade or is_earned:
                completed_courses.append(full_code)

        # Remove duplicates and return
        return list(set(completed_courses))

    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return []