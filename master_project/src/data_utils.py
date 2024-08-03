import pandas as pd
import pgeocode
import datetime

# Load data
df_pol = pd.read_csv(r'../data/raw/political_data.csv', index_col=0)
df_dem = pd.read_csv(r'../data/raw/demographic_data.csv', index_col=0)

# Find common IDs
common_ids = df_pol.index.intersection(df_dem.index)

# Filter dataframes
df_pol_filtered = df_pol.loc[common_ids]
df_dem_filtered = df_dem.loc[common_ids]

df_pol_filtered = df_pol_filtered[~df_pol_filtered.index.duplicated(keep='last')]
df_dem_filtered = df_dem_filtered[~df_dem_filtered.index.duplicated(keep='last')]

# Combine dataframes
df_combi = pd.concat([df_pol_filtered, df_dem_filtered], axis=1)

# Map political views
pol_map = {"0-Left": "Extreme Left",
           "1": "Far Left",
           "2": "Left",
           "3": "Center-Left",
           "4": "Left Leaning",
           "5": "Center",
           "6": "Right Leaning",
           "7": "Center-Right",
           "8": "Right",
           "9": "Far Right",
           "10-Right": "Extreme Right"}

columns_to_map_pol = [df_combi.columns[0], df_combi.columns[1], df_combi.columns[2]]
for column in columns_to_map_pol:
    df_combi[column] = df_combi[column].map(pol_map)

# Map origins
origin_map = {"Yes": "born in the U.S.",
              "No": "born outside the U.S."}
columns_to_map_origin = [df_combi.columns[6], df_combi.columns[7], df_combi.columns[8]]
for column in columns_to_map_origin:
    df_combi[column] = df_combi[column].map(origin_map)

# Filter based on political view
political_view_column = df_combi.columns[2]
df_combi = df_combi[df_combi[political_view_column].isin(["Extreme Left", "Far Left", "Far Right", "Extreme Right"])]

# Filter out rows where both voting responses are "Unknown"
vote_last_election_column = df_combi.columns[3] # replace with actual column name
vote_next_election_column = df_combi.columns[4]  # replace with actual column name

df_combi = df_combi[~((df_combi[vote_last_election_column] == 'Unknown') & (df_combi[vote_next_election_column] == 'Unknown'))]

# Remove rows with any NaN values
df_combi = df_combi.dropna()

# Get coordinates of cities based on ZIP code
nomi = pgeocode.Nominatim('us')
zip_cache = {}

def find_location(zip_code):
    if zip_code in zip_cache:
        return zip_cache[zip_code]
    location = nomi.query_postal_code(zip_code)
    if pd.notna(location['place_name']) and pd.notna(location['state_name']):
        city_state = f"{location['place_name']}, {location['state_name']}"
    else:
        city_state = f"a location in the U.S. with the following ZIP code: {zip_code}"
    zip_cache[zip_code] = city_state
    return city_state

zip_code_column = df_combi.columns[-2]  # replace with actual column name
try:
    df_combi[zip_code_column] = df_combi[zip_code_column].apply(find_location)
except KeyError:
    print("KeyError: 'zip_code' column not found in the dataframe")
    print("Please make sure the column name is correct and try again")

# Calculate ages
year_cache = {}
current_year = datetime.datetime.now().year

def calculate_age(year_of_birth):
    if year_of_birth in year_cache:
        return year_cache[year_of_birth]
    try:
        age = str(current_year - int(year_of_birth)) + " years old"
    except ValueError:
        age = "were born in the year " + year_of_birth
    return age

year_of_birth_column = df_combi.columns[-1]  # replace with actual column name
try:
    df_combi[year_of_birth_column] = df_combi[year_of_birth_column].apply(calculate_age)
except KeyError:
    print("KeyError: 'year_of_birth' column not found in the dataframe")
    print("Please make sure the column name is correct and try again")

# Save the resulting dataframe to a CSV file
df_combi.to_csv(r'../data/processed/combined_data.csv')


