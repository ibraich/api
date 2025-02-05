from flask import current_app
from werkzeug.exceptions import BadRequest
import requests


class F1ScoreService:

    def __init__(self):
        pass

    def get_f1_score(self, f1_score_request_dto):
        # Define the base URL
        url = current_app.config.get("DIFFERENCE_CALC_URL") + "/f1-score"
        # Define the headers
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        response = requests.post(url, json=f1_score_request_dto, headers=headers)
        if response.status_code != 200:
            raise BadRequest("Failed to fetch f1 score: " + response.text)
        f1_score = response.json()
        return f1_score


f1_score_service = F1ScoreService()
