import os
import json
import pytest
from fastapi.testclient import TestClient
from ..main import app
from .. import storage

# Mock data directory for testing
TEST_DATA_DIR = "llm-council/data/test_conversations"

@pytest.fixture(autouse=True)
def setup_test_data(monkeypatch):
    """Set up a temporary data directory for testing."""
    if not os.path.exists(TEST_DATA_DIR):
        os.makedirs(TEST_DATA_DIR)
    
    # Mock DATA_DIR in storage and config
    monkeypatch.setattr(storage, "DATA_DIR", TEST_DATA_DIR)
    
    # Create some test conversations
    conv1 = {
        "id": "test-1",
        "created_at": "2026-01-01T10:00:00Z",
        "title": "Quantum Physics Basics",
        "messages": [{"role": "user", "content": "What is quantum physics?"}]
    }
    conv2 = {
        "id": "test-2",
        "created_at": "2026-01-02T10:00:00Z",
        "title": "Baking a Cake",
        "messages": [{"role": "user", "content": "How to bake a chocolate cake?"}]
    }
    
    with open(os.path.join(TEST_DATA_DIR, "test-1.json"), "w") as f:
        json.dump(conv1, f)
    with open(os.path.join(TEST_DATA_DIR, "test-2.json"), "w") as f:
        json.dump(conv2, f)
        
    yield
    
    # Cleanup
    for f in os.listdir(TEST_DATA_DIR):
        os.remove(os.path.join(TEST_DATA_DIR, f))
    os.rmdir(TEST_DATA_DIR)

client = TestClient(app)

def test_list_conversations():
    """Test that conversations are listed correctly."""
    response = client.get("/api/conversations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Should be sorted newest first
    assert data[0]["id"] == "test-2"
    assert data[1]["id"] == "test-1"
    assert data[0]["title"] == "Baking a Cake"

def test_get_conversation():
    """Test retrieving a specific conversation."""
    response = client.get("/api/conversations/test-1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-1"
    assert data["title"] == "Quantum Physics Basics"
    assert len(data["messages"]) == 1

def test_get_conversation_not_found():
    """Test error handling for non-existent conversation."""
    response = client.get("/api/conversations/non-existent")
    assert response.status_code == 404

def test_search_conversations():
    """
    Test searching conversations.
    THIS IS EXPECTED TO FAIL (Red Phase) as 'search' param is not yet implemented.
    """
    # Search for 'Physics'
    response = client.get("/api/conversations?search=Physics")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "test-1"
    
def test_search_conversations_content():
    """Test searching for content within messages."""
    # Search for 'chocolate'
    response = client.get("/api/conversations?search=chocolate")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "test-2"

def test_update_title():
    """Test updating a conversation title."""
    # This might require a new endpoint or direct storage call test
    storage.update_conversation_title("test-1", "New Quantum Title")
    response = client.get("/api/conversations/test-1")
    assert response.status_code == 200
    assert response.json()["title"] == "New Quantum Title"

def test_create_conversation():
    """Test creating a new conversation."""
    response = client.post("/api/conversations", json={})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["title"] == "New Conversation"
    assert data["messages"] == []
