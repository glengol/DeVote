# import pytest
# import requests
# import os

# @pytest.fixture
# def url():
#     return "http://localhost:5000"

# def test_vote_submission(url):
#     data = {
#         'name': 'TestUser',
#     }
#     response = requests.post(url + "/vote", data=data)
#     assert response.status_code == 200
#     assert "Hello, TestUser" in response.text
