# import pytest
# import requests
# import os

# @pytest.fixture
# def url():
#     return "http://localhost:5000"  

# def test_results_page(url):
#     response = requests.get(url + "/results")
#     assert response.status_code == 200
#     assert "Results" in response.text
#     assert "Charts" in response.text
#     assert "Recent Comments" in response.text
