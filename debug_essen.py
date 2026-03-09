import json
import re

with open("data.js", "r", encoding="utf-8") as f:
    text = f.read()

# Extract json part
json_part = text.replace("const SCHOOL_DATA = ", "").strip()
if json_part.endswith(";"):
    json_part = json_part[:-1]

data = json.loads(json_part)

essen_schools = [s for s in data if s['City'] == 'Essen']

print(f"Total Essen schools in data.js: {len(essen_schools)}")

# Count how many have valid lat/lon native vs fallback
has_lat = sum(1 for s in essen_schools if 'lat' in s)
print(f"Essen schools with geocoded lat/lon: {has_lat}")
print(f"Essen schools missing geocoded lat/lon: {len(essen_schools) - has_lat}")

# Print a few to see what names they have
for s in essen_schools[:10]:
    print(f"- {s['Schulname']} (Index {s.get('Index_25_26')})")


