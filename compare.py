import pandas as pd
import json

def compare_data():
    df24 = pd.read_csv("data_24_25.csv", dtype={'Schulnummer': str, 'Sozialindex': str})
    df25 = pd.read_csv("data_25_26.csv", dtype={'Schulnummer': str, 'Sozialindex': str})
    
    # Filter for target cities as specified in step 3
    target_cities = ['Essen', 'Ratingen', 'Bochum', 'Dortmund', 'Witten', 'Herdecke']
    
    # Function to check if Kreis contains target city
    def is_target(kreis):
        if pd.isna(kreis): return False
        # Sometimes it says "Dortmund", sometimes "Bochum", sometimes it's in Ennepe-Ruhr-Kreis (for Witten, Herdecke), Mettmann for Ratingen
        # Since 'Kreis' might just be the county name, we will leave the filtering for the map phase, but let's pre-filter the output for the map.
        return True

    # Rename columns for joining
    df24.rename(columns={'Sozialindex': 'Index_24_25'}, inplace=True)
    df25.rename(columns={'Sozialindex': 'Index_25_26'}, inplace=True)
    
    # Merge on Schulnummer
    merged = pd.merge(df25, df24[['Schulnummer', 'Index_24_25']], on='Schulnummer', how='left')
    
    # Fill NaN for missing previous index
    merged['Index_24_25'].fillna('Neu', inplace=True)
    
    # Calculate difference
    # Note: 'ohne' needs to be handled
    def calc_diff(row):
        i24 = row['Index_24_25']
        i25 = row['Index_25_26']
        if i24 == 'Neu' or i24 == 'ohne' or i25 == 'ohne':
            return 'N/A'
        try:
            return int(i25) - int(i24)
        except:
            return 'N/A'
            
    merged['Difference'] = merged.apply(calc_diff, axis=1)
    
    # Find schools in target cities based on Schulname or Kreis
    # Witten and Herdecke are in Ennepe-Ruhr-Kreis
    # Ratingen is in Kreis Mettmann
    def match_city(row):
        kreis = str(row['Kreis']).lower()
        name = str(row['Schulname']).lower()
        for city in target_cities:
            c = city.lower()
            if c in kreis or c in name:
                return city
        return None
        
    merged['City'] = merged.apply(match_city, axis=1)
    
    # Filter to only the target cities
    filtered = merged[merged['City'].notnull()].copy()
    
    # Save the filtered results for the next step (geocoding)
    filtered.to_json("filtered_schools.json", orient='records', force_ascii=False, indent=2)
    filtered.to_csv("filtered_schools.csv", index=False)
    
    print(f"Total schools in NRW: {len(df25)}")
    print(f"Total schools in target cities: {len(filtered)}")
    
    # Print some stats for the target cities
    print(filtered['City'].value_counts())

if __name__ == "__main__":
    compare_data()
