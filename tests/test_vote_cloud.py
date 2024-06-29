import pytest
import requests

@pytest.fixture
def url():
    return "http://localhost:5000"  

def test_vote_cloud_selection(url):
    data = {
        'name': 'TestUser',
        'choice_Which cloud provider do you prefer?': 'AWS',
    }
    response = requests.post(url + "/vote_cloud", data=data)
    assert response.status_code == 200
    assert "Choose your favorite services from AWS" in response.text
