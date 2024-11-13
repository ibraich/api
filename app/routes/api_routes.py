from . import main
from flask import jsonify

@main.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"message": "Nlp project backend"})