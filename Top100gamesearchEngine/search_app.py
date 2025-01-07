from flask import Flask, request, render_template
from elasticsearch import Elasticsearch
import math

# Elasticsearch connection
ELASTIC_PASSWORD = "ab1234"
es = Elasticsearch("https://localhost:9200", http_auth=("elastic", ELASTIC_PASSWORD), verify_certs=False)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Search route to fetch data from Elasticsearch and display in the template
@app.route('/search')
def search():
    page_size = 10  # Number of items per page
    keyword = request.args.get('keyword')  # Search keyword from user input
    page_no = int(request.args.get('page', 1))  # Page number (default is 1)

    # Elasticsearch query to search for products by keyword in 'name' and 'description' fields
    body = {
        'size': page_size,
        'from': page_size * (page_no - 1),
        'query': {
            'multi_match': {
                'query': keyword,
                'fields': ['name^3', 'description', 'tag']
            }
        }
    }

    # Perform the search on Elasticsearch
    res = es.search(index='gameindex4', body=body)

    # Extract relevant data from the search response
    hits = [{
        'name': doc['_source']['name'],
        'description': doc['_source']['description'],
        'image': doc['_source'].get('image', ''),  # Provide a default if no image exists
        'price': doc['_source'].get('price', 'N/A'),
        'tag': doc['_source'].get('tag', 'No Tags'),
        'score': doc['_score'],  # Fixed the extra single quote here
        'url': doc['_source'].get('url', '#') 
    } for doc in res['hits']['hits']]

    # Calculate total number of pages
    page_total = math.ceil(res['hits']['total']['value'] / page_size)

    # Render the search results page with the fetched data
    return render_template('index.html', keyword=keyword, hits=hits, page_no=page_no, page_total=page_total)

if __name__ == '__main__':
    app.run(debug=True)
