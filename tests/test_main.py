from fastapi.testclient import TestClient
from app.main import todo_server

client = TestClient(app =  todo_server)

def test_hello():
    gree: str = "Hi"
    assert gree == "Hi"


def test_fastapi_hello():
    response = client.get("/")
    assert response.json() == {"Greet": "Hello World!"}



