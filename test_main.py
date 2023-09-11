import json

from fastapi.testclient import TestClient
from main import app, extract_themes

client = TestClient(app)

sample_text = """This is an artificial intelligence example. Machine learning drives AI in numerous ways."""

def test_extract_themes():
    themes = extract_themes(sample_text)
    assert "loan" in [theme for theme in themes]

def test_add_themes():
    client.headers["Content-Type"] = "application/json"
    response = client.post("/themes", json={"url": "https://en.wikipedia.org/wiki/Artificial_intelligence"})
    data = json.loads(response.text)
    assert response.status_code == 200
    assert "themes" in data["message"]