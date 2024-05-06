import json
import pandas as pd
import logging
from datetime import datetime, timedelta

logger = logging.getLogger()


def main(input_file, output_file):
    data = pd.read_csv(input_file)

    # Convert the 'Date first seen' column to datetime format
    data['Date first seen'] = pd.to_datetime(data['Date first seen'])

    # Extract day, year, and month from the 'Date first seen' column
    data['Day'] = data['Date first seen'].dt.day
    data['Year'] = data['Date first seen'].dt.year
    data['Month'] = data['Date first seen'].dt.month

    # Drop the specified columns
    columns_to_drop = ['attackType', 'attackID', 'attackDescription']
    data = data.drop(columns=columns_to_drop)

    # Save the preprocessed data to a new CSV file
    data.to_csv(output_file, index=False)

if __name__ == "__main__":

    test_json_path = "data/test_details.json"
    with open(test_json_path) as f:
        json_data = json.load(f)
        dataframe = main(json_data)
