import pandas as pd
import requests
import io
import json
from pyproj import Transformer

def fetch_and_merge():
    url = "https://www.schulministerium.nrw.de/BiPo/OpenData/Schuldaten/schuldaten.csv"
    print("Downloading official school data...")
    response = requests.get(url)
    response.raise_for_status()
    
    lines = response.text.splitlines()
    if lines[0].startswith("sep="):
        lines = lines[1:]
        
    csv_text = "\n".join(lines)
    df_geo = pd.read_csv(io.StringIO(csv_text), sep=';', dtype=str, encoding='utf-8')
    print(f"Loaded {len(df_geo)} rows from official data.")
    
    # Transformer from EPSG:25832 (UTM Zone 32N) to EPSG:4326 (WGS84 Lat/Lon)
    transformer = Transformer.from_crs("EPSG:25832", "EPSG:4326", always_xy=True)
    
    geo_dict = {}
    for _, row in df_geo.iterrows():
        s_num = str(row['Schulnummer']).strip()
        easting = row['UTMRechtswert']
        northing = row['UTMHochwert']
        if pd.notna(easting) and pd.notna(northing):
            try:
                lon, lat = transformer.transform(float(easting), float(northing))
                geo_dict[s_num] = {'lat': lat, 'lon': lon}
            except Exception:
                pass

    # Now load our filtered schools (which has 388 schools including Essen)
    with open("filtered_schools.json", "r", encoding="utf-8") as f:
        all_schools = json.load(f)
        
    essen_schools = []
    
    for s in all_schools:
        if s['City'] == 'Essen':
            s_num = str(s['Schulnummer']).strip()
            if s_num in geo_dict:
                s['lat'] = geo_dict[s_num]['lat']
                s['lon'] = geo_dict[s_num]['lon']
            else:
                print(f"Warning: No official coord for {s_num} - {s['Schulname']}")
            essen_schools.append(s)

    with open("essen_data.js", "w", encoding="utf-8") as f:
        f.write("const SCHOOL_DATA = ")
        json.dump(essen_schools, f, ensure_ascii=False, indent=2)
        f.write(";\n")
        
    print(f"Created essen_data.js with {len(essen_schools)} Essen schools using official coordinates.")

if __name__ == "__main__":
    fetch_and_merge()
