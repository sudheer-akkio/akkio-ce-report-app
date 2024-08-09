import os

from src.utils import PPTXExporter

# Setup
artifacts_folder = os.path.join(os.getcwd(), "artifacts")

# Initialize object
obj = PPTXExporter(artifacts_folder)

# Create slides
obj.create()

# Save the presentation
pptx_fname = "output_deck.pptx"

obj.save(pptx_fname)
