import pdfplumber
import re
import pandas as pd
import sys

def parse_pdf(pdf_path):
    print(f"Parsing {pdf_path}...")
    
    current_br = None
    current_kreis = None
    current_schulform = None
    
    # Matching the school line with optional Prefix text before the Schulnummer
    # Pattern: [Options Prefix] [Schulnummer: 6 digits maybe with space] [Schulname] [Index: 1-9 or 'ohne']
    # Example 1: BR Arnsberg Ennepe-Ruhr-Kreis Grundschule 131209 Witten, GG Bruch 4
    # Example 2: 13 1210 Witten, GG Crengeldanzschule 6
    # Example 3: Realschule 194141 Witten, RS Helene-Lohmann-Realschule 3
    
    full_pattern = re.compile(r'^(.*?)\b(\d{2}\s?\d{4})\s+(.+?)\s+(\d|ohne)$')
    
    parsed_data = []

    with pdfplumber.open(pdf_path) as pdf:
        # Tables start around page 6
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text: continue
            
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if not line: continue
                # Skip header/footer
                if "Vorabinformation" in line or "Sozialindexstufe" in line or "Schulnummer" in line or "Übersicht über die" in line or "und Schulform ab" in line:
                    continue
                
                match = full_pattern.search(line)
                if match:
                    prefix_text = match.group(1).strip()
                    schulnummer = match.group(2).replace(" ", "")
                    schulname = match.group(3).strip()
                    index = match.group(4).strip()
                    
                    if prefix_text:
                        # Find BR, Kreis, Schulform if they are in the prefix
                        # Typically it's "BR <Name> <Kreis> <Schulform>"
                        # Let's split by known Schulformen
                        schulformen = ['Grundschule', 'Hauptschule', 'Realschule', 'Sekundarschule', 'Gesamtschule', 'Gymnasium', 'Förderschule', 'PRIMUS', 'Gemeinschaftsschule', 'Weiterbildungskolleg', 'Berufskolleg']
                        found_sf = None
                        for sf in schulformen:
                            if sf in prefix_text:
                                found_sf = sf
                                break
                        
                        if found_sf:
                            current_schulform = found_sf
                            prefix_before_sf = prefix_text.split(found_sf)[0].strip()
                            if prefix_before_sf:
                                if prefix_before_sf.startswith("BR "):
                                    # Split BR and Kreis
                                    parts = prefix_before_sf.split(" ", 2)
                                    if len(parts) >= 3:
                                        current_br = parts[0] + " " + parts[1]
                                        current_kreis = parts[2].strip()
                                    else:
                                        # handle anomaly
                                        current_kreis = prefix_before_sf.replace(current_br, "").strip() if current_br else prefix_before_sf
                                else:
                                    current_kreis = prefix_before_sf
                        else:
                            # It might just be Kreis or BR change without Schulform
                            if prefix_text.startswith("BR "):
                                current_br = prefix_text
                            else:
                                current_kreis = prefix_text
                                
                    parsed_data.append({
                        'Bezirksregierung': current_br,
                        'Kreis': current_kreis,
                        'Schulform': current_schulform,
                        'Schulnummer': schulnummer,
                        'Schulname': schulname,
                        'Sozialindex': index
                    })

    return pd.DataFrame(parsed_data)

if __name__ == "__main__":
    df_24_25 = parse_pdf("24_25.pdf")
    df_24_25.to_csv("data_24_25.csv", index=False)
    print(f"Saved data_24_25.csv with {len(df_24_25)} rows.")
    
    df_25_26 = parse_pdf("25_26.pdf")
    df_25_26.to_csv("data_25_26.csv", index=False)
    print(f"Saved data_25_26.csv with {len(df_25_26)} rows.")
