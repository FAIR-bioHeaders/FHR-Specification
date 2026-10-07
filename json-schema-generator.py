import json
import os
from linkml_runtime import SchemaView
from linkml.generators.jsonschemagen import JsonSchemaGenerator

# Define the path to the LinkML schema file
linkml_schema_path = 'fhr_linkml.yml'

# Load the LinkML schema
schema_view = SchemaView(linkml_schema_path)

# Generate the JSON Schema
json_schema_generator = JsonSchemaGenerator(
    schema_view.schema, include_null=False, not_closed=False
)
json_schema = json.loads(json_schema_generator.serialize())
for slot_name in schema_view.class_slots('FHR'):
    slot_range = schema_view.induced_slot(slot_name, 'FHR').range
    if slot_range in schema_view.all_classes():
        json_schema['$defs'][slot_range].pop('additionalProperties', None)
json_schema = json.dumps(json_schema, indent=4)

# Define the output path for the JSON Schema file
json_schema_output_path = 'fhr_linkml.json'

# Write the JSON Schema to the file
with open(json_schema_output_path, 'w') as json_file:
    json_file.write(json_schema)

print(f"JSON Schema has been successfully generated and saved to {json_schema_output_path}")
