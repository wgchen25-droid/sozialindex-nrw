import json
import time
import os
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

def geocode_schools():
    with open("filtered_schools.json", "r", encoding="utf-8") as f:
        schools = json.load(f)
        
    # Load existing geocoded data to avoid re-geocoding
    existing_geocodes = {}
    if os.path.exists("geocoded_schools.json"):
        with open("geocoded_schools.json", "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                for s in data:
                    if 'lat' in s and 'lon' in s:
                        existing_geocodes[s['Schulnummer']] = (s['lat'], s['lon'])
            except:
                pass
        
    geolocator = Nominatim(user_agent="sozial_index_mapper_nrw_2026_v2")
    
    geocoded_schools = []
    not_found = 0
    
    print(f"Geocoding {len(schools)} schools (skipping {len(existing_geocodes)} already geocoded)...")
    
    for i, school in enumerate(schools):
        if school['Schulnummer'] in existing_geocodes:
            # Already have it
            lat, lon = existing_geocodes[school['Schulnummer']]
            school['lat'] = lat
            school['lon'] = lon
            geocoded_schools.append(school)
            continue
            
        # Construct address
        city = school['City']
        name = school['Schulname']
        
        # Clean name if it starts with city name
        clean_name = name
        if clean_name.lower().startswith(city.lower() + ", "):
            clean_name = clean_name[len(city) + 2:]
        elif clean_name.lower().startswith(city.lower() + " "):
            clean_name = clean_name[len(city) + 1:]
            
        clean_name = clean_name.replace("GG ", "Gemeinschaftsgrundschule ")
        clean_name = clean_name.replace("KG ", "Katholische Grundschule ")
        clean_name = clean_name.replace("EGS ", "Evangelische Grundschule ")
        clean_name = clean_name.replace("RS ", "Realschule ")
        clean_name = clean_name.replace("GE ", "Gesamtschule ")
        clean_name = clean_name.replace("Gym ", "Gymnasium ")
        clean_name = clean_name.replace("SK ", "Sekundarschule ")
        clean_name = clean_name.replace("GH ", "Gemeinschaftshauptschule ")
        clean_name = clean_name.replace("KH ", "Katholische Hauptschule ")
        clean_name = clean_name.replace("(Verb.) ", "")
        
        queries = [
            f"{clean_name}, {city}, Nordrhein-Westfalen, Germany",
            f"{school['Schulform']} {clean_name}, {city}, Germany",
            f"{name}, {city}, Germany"
        ]
        
        location = None
        for q in queries:
            try:
                time.sleep(1)
                location = geolocator.geocode(q, timeout=10)
                if location:
                    break
            except (GeocoderTimedOut, GeocoderServiceError) as e:
                time.sleep(2)
        
        if location:
            school['lat'] = location.latitude
            school['lon'] = location.longitude
            print(f"[{i+1}/{len(schools)}] SUCCESS: {name} in {city} -> {location.latitude}, {location.longitude}")
        else:
            print(f"[{i+1}/{len(schools)}] FAILED: {name} in {city}")
            not_found += 1
            
        geocoded_schools.append(school)
        
        # Save intermediate results every 10 schools to avoid losing data
        if (i + 1) % 10 == 0:
            with open("geocoded_schools.json", "w", encoding="utf-8") as f:
                json.dump(geocoded_schools, f, ensure_ascii=False, indent=2)
                
    # Final save
    with open("geocoded_schools.json", "w", encoding="utf-8") as f:
        json.dump(geocoded_schools, f, ensure_ascii=False, indent=2)
        
    print(f"Geocoding complete. {not_found} schools not found.")

if __name__ == "__main__":
    geocode_schools()
