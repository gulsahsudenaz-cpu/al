"""
Chat API Tests
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app

client = TestClient(app)


def test_create_chat():
    """Test creating a new chat"""
    response = client.post(
        "/v1/chat/chats",
        json={"tenant": "test-tenant"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["status"] == "active"


def test_create_chat_with_metadata():
    """Test creating a chat with metadata"""
    response = client.post(
        "/v1/chat/chats",
        json={"tenant": "test-tenant", "metadata": {"key": "value"}}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data


def test_create_chat_invalid_tenant():
    """Test creating a chat with invalid tenant"""
    # Empty tenant
    response = client.post(
        "/v1/chat/chats",
        json={"tenant": ""}
    )
    assert response.status_code == 422
    
    # Tenant too long
    response = client.post(
        "/v1/chat/chats",
        json={"tenant": "a" * 200}
    )
    assert response.status_code == 422


def test_get_chat_not_found():
    """Test getting a non-existent chat"""
    fake_id = str(uuid4())
    response = client.get(f"/v1/chat/chats/{fake_id}")
    assert response.status_code == 404


def test_create_message_invalid_text():
    """Test creating a message with invalid text"""
    # Create a chat first
    chat_response = client.post(
        "/v1/chat/chats",
        json={"tenant": "test-tenant"}
    )
    chat_id = chat_response.json()["id"]
    
    # Empty text
    response = client.post(
        f"/v1/chat/chats/{chat_id}/messages",
        json={"text": ""}
    )
    assert response.status_code == 422
    
    # Text too long
    response = client.post(
        f"/v1/chat/chats/{chat_id}/messages",
        json={"text": "a" * 10000}
    )
    assert response.status_code == 422


def test_create_message_chat_not_found():
    """Test creating a message for a non-existent chat"""
    fake_id = str(uuid4())
    response = client.post(
        f"/v1/chat/chats/{fake_id}/messages",
        json={"text": "Hello"}
    )
    assert response.status_code == 404

