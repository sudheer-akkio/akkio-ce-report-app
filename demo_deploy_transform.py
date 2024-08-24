import json
import os
import time

import akkio
import pandas as pd
import requests

from src import utils

API_KEY = "463c3703-cb1d-434b-a540-bbcb4b5db0d7"

utils.API_KEY = API_KEY
akkio.api_key = API_KEY

project_id = "9fa0ce02-46c9-48da-9f5c-3ad4cceb4004"  # This project should be locked in production


# import raw data
filename = "Sales_Data_Test.csv"

filepath = os.path.join(os.getcwd(), "data", filename)

in_df = utils.import_data(filepath)

in_df_dict = utils.df_to_dict(in_df)

transformed_df = utils.transform_data(project_id, in_df_dict, save=True)

# Create and add rows to dataset -- create new utility function
dataset_name = "transformed_sales_data_5"
transformed_dataset_id = utils.create_dataset(dataset_name, transformed_df)

print(f"Transformed dataset id: {transformed_dataset_id}")

# train model to force project creation -- returns projectID = modelID
# Train ML Model
# (Train a dummy model to force project creation in the UI (I know this is suboptimal, but we will optimize this out in our v2 API))

# UI Mapping:
#     1    = Super Fast (Do not recommend)
#     10   = Fastest
#     60   = High Quality
#     300  = Higher Quality
#     1800 = Production

training_mode = 1
predict_field = ["Sales"]
ignore_fields = []

# Can grab an existing dataset ID if needed so you don't have to recreated datasets each time. This is found in the Datasets tab in Akkio
# dataset_id = ""

new_model = akkio.create_model(
    transformed_dataset_id,
    predict_field,
    ignore_fields,
    {"duration": training_mode, "extra_attention": False},
)

# grab project id from new_model
transformed_project_id = new_model["model_id"]

print(f"Transformed Data Project ID: {transformed_project_id}")
