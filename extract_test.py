import pdfplumber
import re
import json

def parse_pdf(pdf_path):
    print(f"Parsing {pdf_path}...")
    
    current_br = None
    current_kreis = None
    current_schulform = None
    
    # Regex to match a line that starts with a Schulnummer (6 digits, allowing for a space)
    # Examples: "131209 Witten, GG Bruch 4", "13 1210 Witten, GG Crengeldanzschule 6"
    school_pattern = re.compile(r'^(\d{2}\s?\d{4})\s+(.+?)\s+(\d|ohne)$')
    
    parsed_data = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages[5:8], start=6):
            text = page.extract_text()
            if not text: continue
            
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if not line or "Vorabinformation" in line or "Sozialindexstufe" in line or "Schulnummer" in line:
                    continue
                
                # Check if line starts with BR 
                if line.startswith("BR "):
                    parts = line.split(" ", 2)
                    # Line might be "BR Arnsberg Ennepe-Ruhr-Kreis Grundschule 131209 Witten, GG Bruch 4"
                    # This tells us we need a more robust parsing mechanism because multiple fields are on the same line
                    print(f"DEBUG BR line: {line}")
                
                match = school_pattern.search(line)
                if match:
                    # It's merely a school line
                    # print(f"Found school: {match.groups()}")
                    pass
                else:
                    # Might be a Schulform change, e.g., "Realschule 194141 Witten, RS Helene-Lohmann-Realschule 3"
                    # print(f"Other line: {line}")
                    pass

if __name__ == "__main__":
    parse_pdf("24_25.pdf")
