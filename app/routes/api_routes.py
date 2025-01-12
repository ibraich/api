from . import main
from flask import request,jsonify
from app.services.document_recommendation_service import DocumentRecommendationService


@main.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"message": "Nlp project backend"})

recommendation_service = DocumentRecommendationService()
def review_recommendation(recommendation_id):
    try:
        action = request.json.get('action')
        if action not in ['accept', 'reject']:
            return jsonify({"error": "Invalid action. Must be 'accept' or 'reject'."}), 400

        if action == 'accept':
            result = recommendation_service.accept_recommendation(recommendation_id)
        else:
            result = recommendation_service.reject_recommendation(recommendation_id)

        return jsonify({"success": True, "result": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Adding the route to the existing API routes
def register_routes(app):
    app.add_url_rule(
        '/recommendations/<int:recommendation_id>/review', 'review_recommendation', review_recommendation, methods=['POST']
    )