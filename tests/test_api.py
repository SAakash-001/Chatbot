import sys
import os
import unittest
from fastapi.testclient import TestClient
import json

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from main import app
except ImportError as e:
    print(f"Error importing app from main: {e}")
    raise

class TestAPIEndpoints(unittest.TestCase):
    """Test the API endpoints of the SciPris chatbot."""
    
    def setUp(self):
        """Set up the test client and necessary test data."""
        self.client = TestClient(app)
        
    def test_healthcheck(self):
        """Test the healthcheck endpoint returns correct status."""
        response = self.client.get("/healthcheck")
        
        # Check response code and content
        self.assertEqual(response.status_code, 200)
        
        # Parse response JSON
        data = response.json()
        
        # Verify required fields
        self.assertIn("status", data)
        self.assertIn("database", data)
        self.assertIn("active_sessions", data)
        self.assertIn("uptime", data)
        
        # Verify values
        self.assertEqual(data["status"], "ok")
        
    def test_ask_endpoint(self):
        """Test the ask endpoint with a simple query."""
        payload = {
            "message": "What payment methods do you accept?",
            "session_id": None  # Let the server create a new session
        }
        
        response = self.client.post(
            "/ask",
            json=payload
        )
        
        # Check response code
        self.assertEqual(response.status_code, 200)
        
        # Parse response JSON
        data = response.json()
        
        # Verify required fields
        self.assertIn("response", data)
        self.assertIn("session_id", data)
        
        # Verify we got a session ID
        self.assertIsNotNone(data["session_id"])
        
        # Verify response contains payment information
        self.assertIn("payment", data["response"].lower())
        
    def test_session_persistence(self):
        """Test that the session maintains context between requests."""
        # First request to establish session
        first_payload = {
            "message": "What payment methods do you accept?",
            "session_id": None
        }
        
        first_response = self.client.post("/ask", json=first_payload)
        first_data = first_response.json()
        session_id = first_data["session_id"]
        
        # Second request using established session
        second_payload = {
            "message": "Can I pay with PayPal?",
            "session_id": session_id
        }
        
        second_response = self.client.post("/ask", json=second_payload)
        second_data = second_response.json()
        
        # Verify the session ID is maintained
        self.assertEqual(second_data["session_id"], session_id)
        
    def test_feedback_endpoint(self):
        """Test the feedback endpoint."""
        # First create a session
        ask_response = self.client.post("/ask", json={"message": "Hello", "session_id": None})
        session_id = ask_response.json()["session_id"]
        
        # Then submit feedback
        feedback_payload = {
            "session_id": session_id,
            "rating": 5,
            "comments": "Great response!"
        }
        
        response = self.client.post("/feedback", json=feedback_payload)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True})

if __name__ == "__main__":
    unittest.main() 