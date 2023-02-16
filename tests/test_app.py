import pytest
import app
from app import database


@pytest.fixture
def client():
    """Fixture of slack app for client"""
    api_app = app.create_app()
    api_app.config['TESTING'] = True
    database.init_database(api_app)
    yield api_app.test_client()


def test_list_tasks(client):
    """Test listing task."""
    response = client.get('/tasks')
    assert response.status_code == 200
    assert response.json == {'data': []}


def test_create_tak(client):
    """Test creating a task."""
    req = {
        "data": {
            "attributes": {
                "title": "hello wold ubuntu",
                "description": "Run hello world in ubuntu",
                "command": "echo hello world",
                "image": "ubuntu"
            }
        }
    }

    response = client.post('/tasks', json=req)
    assert response.status_code == 201
