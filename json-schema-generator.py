import os
from linkml_runtime import SchemaView
from linkml.generators.jsonschemagen import JsonSchemaGenerator

# Define the path to the LinkML schema file
linkml_schema_path = 'fhr_linkml.yaml'

# Load the LinkML schema
schema_view = SchemaView(linkml_schema_path)

# Generate the JSON Schema
json_schema_generator = JsonSchemaGenerator(schema_view.schema)
json_schema = json_schema_generator.serialize()

# Define the output path for the JSON Schema file
json_schema_output_path = 'fhr_linkml.json'

# Write the JSON Schema to the file
with open(json_schema_output_path, 'w') as json_file:
    json_file.write(json_schema)

print(f"JSON Schema has been successfully generated and saved to {json_schema_output_path}")
