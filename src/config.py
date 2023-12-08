

# Define a function to parse the value based on the key
def parse_value(key, value):
    if key == "DESIRED_SECTIONS":
        # Convert the string to a set of strings, stripping spaces and splitting by commas
        return set(value.replace(" ", "").split(","))
    else:
        # Return the value as a string for all other keys
        return value

# Initialize an empty dictionary to store the configuration
config = {}

# Open the config.txt file and read line by line
with open('config.txt', 'r') as file:
    for line in file:
        # Split the line into key and value parts
        key, value = line.strip().split(' = ')
        # Parse the value and add it to the config dictionary
        config[key] = parse_value(key, value)

# Access the variables from the config dictionary
YEAR = config['YEAR']
TERM = config['TERM']
CAMPUS = config['CAMPUS']
DESIRED_SECTIONS = config['DESIRED_SECTIONS']
NETID = config['NETID']
PASSWORD = config['PASSWORD']

QUERY_PARAMS_SOC_API = {"year": YEAR, "term": TERM, "campus": CAMPUS}


QUERY_PARAMS_WEBREG = {
    "login": "cas",
    "semesterSelection": f"{TERM}{YEAR}",
    "indexList": None,
}

