import pytest
import requests
import os

@pytest.fixture
def url():
    return "http://localhost:5000"

@pytest.fixture(scope='module', autouse=True)
def set_testing_env():
    os.environ['TESTING'] = 'true'
    yield
    del os.environ['TESTING']

def test_index_page(url):
    response = requests.get(url + "/")
    assert response.status_code == 200
    assert "Welcome to DeVote" in response.text

# def test_results_page(url):
#     response = requests.get(url + "/results")
#     assert response.status_code == 200
#     assert "Results" in response.text
#     assert "Charts" in response.text
#     assert "Recent Comments" in response.text

@pytest.mark.parametrize("cloud_provider", ["AWS", "GCP", "Azure", "Alibaba Cloud", "Oracle Cloud"])
def test_vote_cloud_selection(url, cloud_provider):
    data = {
        'name': 'TestUser_' + cloud_provider.replace(" ", "_"),
        'choice_Which cloud provider do you prefer?': cloud_provider,
    }
    response = requests.post(url + "/vote_cloud", data=data)
    assert response.status_code == 200
    assert f"Choose your favorite services from {cloud_provider}" in response.text

# def test_vote_submission(url):
#     data = {
#         'name': 'TestUser',
#     }
#     response = requests.post(url + "/vote", data=data)
#     assert response.status_code == 200
#     assert "Hello, TestUser" in response.text
