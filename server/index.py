from flask import Flask, request, jsonify

from .mapping import get_mapping
from .search import search_items, search_properties

app = Flask(__name__)

@app.route('/items/<item_id>/mapping')
def get_item_mapping(item_id):
    mapping = get_mapping(item_id)
    if mapping:
        return jsonify(mapping)
    return jsonify({'error': 'Item not found'})

@app.route('/properties/<property_id>/mapping')
def get_property_mapping(property_id):
    mapping = get_mapping(property_id)
    if mapping:
        return jsonify(mapping)
    return jsonify({'error': 'Property not found'})

@app.route('/search/items/<label>')
def get_items(label):
    results = search_items(label)
    return jsonify(results)

@app.route('/search/properties/<label>')
def get_properties(label):
    results = search_properties(label)
    return jsonify(results)

