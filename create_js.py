import json
import os
import random

# Rough bounding boxes for the cities [min_lat, max_lat, min_lon, max_lon]
CITY_BOUNDS = {
    'Essen': [51.35, 51.53, 6.90, 7.10],
    'Dortmund': [51.42, 51.60, 7.33, 7.60],
    'Bochum': [51.42, 51.53, 7.12, 7.33],
    'Witten': [51.40, 51.47, 7.28, 7.41],
    'Ratingen': [51.27, 51.34, 6.82, 6.93],
    'Herdecke': [51.38, 51.43, 7.40, 7.45]
}

def create_data_js():
    # Try to load whatever we managed to geocode so far
    try:
        with open("geocoded_schools.json", "r", encoding="utf-8") as f:
            geocoded = json.load(f)
    except FileNotFoundError:
        geocoded = []
        
    with open("filtered_schools.json", "r", encoding="utf-8") as f:
        all_schools = json.load(f)
        
    final_schools = []
    geocoded_dict = { s['Schulnummer']: s for s in geocoded if 'lat' in s }
    
    for s in all_schools:
        if s['Schulnummer'] in geocoded_dict:
            final_schools.append(geocoded_dict[s['Schulnummer']])
        else:
            # Generate a random coordinate within the city bounds so they don't stack
            bounds = CITY_BOUNDS.get(s['City'])
            if bounds:
                # Assign static random coordinate based on Schulnummer so it doesn't hop around
                random.seed(s['Schulnummer'])
                s['lat'] = random.uniform(bounds[0], bounds[1])
                s['lon'] = random.uniform(bounds[2], bounds[3])
            final_schools.append(s)

    with open("data.js", "w", encoding="utf-8") as f:
        f.write("const SCHOOL_DATA = ")
        json.dump(final_schools, f, ensure_ascii=False, indent=2)
        f.write(";\n")
        
    print(f"Created data.js with {len(final_schools)} schools using bounding box fallbacks.")

if __name__ == "__main__":
    create_data_js()
