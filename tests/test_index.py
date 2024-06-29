import pytest
import requests

@pytest.fixture
def url():
    return "http://localhost:5000" 

def test_index_page(url):
    response = requests.get(url + "/")
    assert response.status_code == 200
    assert "Welcome to DeVote" in response.text
