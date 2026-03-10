import json
import os

CITIES = [
    'Essen', 'Bochum', 'Witten', 'Dortmund', 
    'Mülheim', 'Ratingen', 'Hattingen', 
    'Sprockhövel', 'Herdecke'
]

def generate_pages():
    # Load all schools
    with open("all_cities_data.js", "r", encoding="utf-8") as f:
        content = f.read()
        json_str = content.replace("const SCHOOL_DATA = ", "").strip().rstrip(";")
        all_schools = json.loads(json_str)

    # Load template from index.html
    with open("index.html", "r", encoding="utf-8") as f:
        template = f.read()

    # Pre-calculate centers for each city
    # [lat, lon, zoom]
    CITY_CONFIGS = {
        'Essen': [51.4556, 7.0116, 12],
        'Bochum': [51.4818, 7.2162, 12],
        'Dortmund': [51.5136, 7.4653, 12],
        'Witten': [51.4390, 7.3365, 13],
        'Mülheim': [51.4281, 6.8833, 13],
        'Ratingen': [51.2981, 6.8483, 13],
        'Hattingen': [51.3986, 7.1856, 13],
        'Sprockhövel': [51.3486, 7.2483, 13],
        'Herdecke': [51.4019, 7.4331, 14]
    }

    for city in CITIES:
        city_schools = [s for s in all_schools if s['City'] == city]
        filename = f"{city.lower().replace('ö', 'oe')}.html"
        data_filename = f"{city.lower().replace('ö', 'oe')}_data.js"
        
        # Create city-specific data file
        with open(data_filename, "w", encoding="utf-8") as f:
            f.write("const SCHOOL_DATA = ")
            json.dump(city_schools, f, ensure_ascii=False, indent=2)
            f.write(";\n")
            
        # Update template for city
        page_content = template
        page_content = page_content.replace(
            "Sozialindex Schulen Ruhrgebiet 2024-2026", 
            f"Sozialindex Schulen {city} 2024-2026"
        )
        page_content = page_content.replace(
            "Essen, Ratingen, Bochum, Dortmund, Witten, Herdecke",
            f"Stadt {city} (Offizielle Geodaten)"
        )
        
        # Update map center
        config = CITY_CONFIGS.get(city, [51.48, 7.21, 11])
        page_content = page_content.replace(
            "const map = L.map('map').setView([51.4818, 7.2162], 11);",
            f"const map = L.map('map').setView([{config[0]}, {config[1]}], {config[2]});"
        )
        
        # Replace data source
        page_content = page_content.replace(
            '<script src="data.js"></script>',
            f'<script src="{data_filename}"></script>'
        )
        
        # Auto-select city in filter
        # find <option value="Essen">Essen</option>
        # Add all cities to the filter list dynamically in the template or just hide it
        # Let's hide the city filter for individual city pages
        page_content = page_content.replace(
            '<div class="filter-group">',
            '<div class="filter-group" style="display: none;">'
        )

        with open(filename, "w", encoding="utf-8") as f:
            f.write(page_content)
            
        print(f"Generated {filename} with {len(city_schools)} schools.")

if __name__ == "__main__":
    generate_pages()
