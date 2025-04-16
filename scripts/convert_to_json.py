import json

def convert_lat_lon(coord):
    """
    Convert latitude or longitude string to a float.
    Example: "28.3N" -> 28.3, "94.8W" -> -94.8
    """
    try:
        value = float(coord[:-1])
        direction = coord[-1].upper()
        if direction in ['S', 'W']:
            value = -value
        return value
    except Exception as e:
        print(f"Error converting coordinate {coord}: {e}")
        return None

def process_hurdat2(input_file, output_file):
    storms = []
    with open(input_file, 'r') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        header_line = lines[i].strip()
        if not header_line:
            i += 1
            continue

        # The header line is assumed to be formatted as:
        # StormID, Name, Number_of_Records, [Additional Info...]
        header_parts = [part.strip() for part in header_line.split(',')]
        if len(header_parts) < 3:
            print(f"Skipping malformed header: {header_line}")
            i += 1
            continue

        storm_id = header_parts[0]
        storm_name = header_parts[1]
        try:
            num_entries = int(header_parts[2])
        except ValueError:
            print(f"Error converting number of records in header: {header_line}")
            i += 1
            continue

        # Create a dictionary for the storm header
        storm = {
            "id": storm_id,
            "name": storm_name,
            "num_entries": num_entries,
            "observations": []
        }
        i += 1  # Move to the first observation record

        # Process the subsequent num_entries observation lines
        for j in range(num_entries):
            if i >= len(lines):
                break
            data_line = lines[i].strip()
            i += 1

            # Each observation is assumed to be in the format:
            # Date, Time, Record Identifier, System Status, Latitude, Longitude, Max Wind, Min Pressure, (additional fields...)
            data_parts = [part.strip() for part in data_line.split(',')]
            if len(data_parts) < 8:
                print(f"Skipping incomplete observation: {data_line}")
                continue

            observation = {
                "date": data_parts[0],
                "time": data_parts[1],
                "record_identifier": data_parts[2],
                "system_status": data_parts[3],
                "latitude": convert_lat_lon(data_parts[4]),
                "longitude": convert_lat_lon(data_parts[5]),
                "wind": None,
                "pressure": None
            }
            # Convert wind speed and pressure if possible
            try:
                observation["wind"] = int(data_parts[6])
            except ValueError:
                observation["wind"] = None
            try:
                observation["pressure"] = int(data_parts[7])
            except ValueError:
                observation["pressure"] = None

            # You can add parsing for any additional fields here if needed

            storm["observations"].append(observation)

        storms.append(storm)

    # Write the processed data to a JSON file
    with open(output_file, 'w') as f_out:
        json.dump(storms, f_out, indent=4)
    
    print(f"Processed {len(storms)} storms into {output_file}")

if __name__ == '__main__':
    # Adjust these paths as needed for your project folder structure
    input_path = 'data/raw/rawdata.rtf'
    output_path = 'data/processed/hurdat2.json'
    process_hurdat2(input_path, output_path)