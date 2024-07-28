# import pytest
# import requests
# import os

# @pytest.fixture
# def url():
#     return "http://localhost:5000"

# @pytest.mark.parametrize("cloud_provider", ["AWS", "GCP", "Azure", "Alibaba Cloud", "Oracle Cloud"])
# def test_vote_cloud_selection(url, cloud_provider):
#     data = {
#         'name': 'TestUser_' + cloud_provider.replace(" ", "_"),
#         'choice_Which cloud provider do you prefer?': cloud_provider,
#     }
#     response = requests.post(url + "/vote_cloud", data=data)
#     assert response.status_code == 200
#     assert f"Choose your favorite services from {cloud_provider}" in response.text
