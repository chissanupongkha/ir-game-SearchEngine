import uuid
import argparse
import json
from elasticsearch import Elasticsearch, helpers
import os

# Elasticsearch connection
es = Elasticsearch("https://localhost:9200", basic_auth=("elastic", "ab1234"), verify_certs=False)

# Argument parser for file and index
parser = argparse.ArgumentParser()
parser.add_argument("--file", required=True, help="Path to the JSON file")
parser.add_argument("--index", required=True, help="Elasticsearch index name")
args = parser.parse_args()

index = args.index
file = args.file

# Check if the file exists
if not os.path.exists(file):
    raise FileNotFoundError(f"File '{file}' not found.")

# Load JSON data from each line in the file
json_docs = []
with open(file) as json_file:
    for line in json_file:
        try:
            json_docs.append(json.loads(line.strip()))  # Each line is a separate JSON object
        except json.JSONDecodeError as e:
            print(f"Error decoding line: {e}")
            continue

def bulk_json_data(json_list, _index):
    for doc in json_list:
        # Generate a unique ID if 'id' is not present in the document
        doc_id = doc.get("id", str(uuid.uuid4()))  # Generate a new UUID if no 'id' is present
        yield {
            "_index": _index,
            "_id": doc_id,  # Use the generated or provided ID
            "_source": doc
        }

# Perform bulk indexing
try:
    response = helpers.bulk(es, bulk_json_data(json_docs, index))
    print("RESPONSE:", response)
except Exception as e:
    print("ERROR:", e)
