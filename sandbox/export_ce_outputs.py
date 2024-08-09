import json
import os

import pandas as pd
import plotly.io as pio

folder_path = os.path.join(os.getcwd(), "chat_response")

filenames = os.listdir(folder_path)
full_file_paths = [os.path.join(folder_path, filename) for filename in filenames]

for fname in full_file_paths:

    # Open the text file in read mode
    with open(fname, "r") as file:
        # Read the content of the file and parse it as JSON
        data = json.load(file)

    raw_message = data["messages"][1]

    output_file_path = os.path.join(os.getcwd(), "artifacts", "ce")

    # Check if 'images' exist in raw_message
    if "images" in raw_message and raw_message["images"]:
        # Deserialize the first image's JSON data
        fig = pio.from_json(raw_message["images"][0])

        # Define desired dimensions and scale
        output_file_path = output_file_path + "_image.png"
        # fig.write_image(output_file_path, width=1920, height=1080, scale=1)

        fig.update_layout(
            xaxis=dict(
                tickangle=-45  # Slant the labels by 45 degrees. You can change this value as needed.
            )
        )

        fig.write_image(output_file_path, width=800, height=600, scale=2)

    # Check if 'table' exists in raw_message
    elif "table" in raw_message and raw_message["table"]:
        # Process table data here

        df = pd.DataFrame(raw_message["table"])

        output_file_path = output_file_path + "_table.csv"

        df.to_csv(output_file_path, index=False)

    # Fallback to process text if no images or table
    else:
        # Process text data here
        output_file_path = output_file_path + "_text.txt"
        with open(output_file_path, "w", encoding="utf-8") as file:
            file.write(raw_message["content"])
