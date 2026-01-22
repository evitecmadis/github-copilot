"""
Tests for the FastAPI application
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    
    # Store original state
    original_activities = {
        "Debate Club": {
            "description": "Develop public speaking and argumentation skills through structured debates",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Stock Market Club": {
            "description": "Learn about investing, trading, and financial markets",
            "schedule": "Mondays, 3:30 PM - 4:30 PM",
            "max_participants": 18,
            "participants": ["james@mergington.edu", "sara@mergington.edu"]
        },
        "Go Club": {
            "description": "Master the ancient game of Go and compete with other players",
            "schedule": "Saturdays, 2:00 PM - 4:00 PM",
            "max_participants": 10,
            "participants": ["kevin@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Reset activities
    activities.clear()
    activities.update(original_activities)
    yield
    # Clean up after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for getting activities"""
    
    def test_get_activities(self, client, reset_activities):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Debate Club" in data
        assert "Chess Club" in data
        assert len(data) == 6
    
    def test_get_activities_contains_details(self, client, reset_activities):
        """Test that activity details are present"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Debate Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


class TestSignup:
    """Tests for signing up for activities"""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup"""
        response = client.post(
            "/activities/Debate Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "test@mergington.edu" in data["message"]
    
    def test_signup_duplicate_email(self, client, reset_activities):
        """Test that duplicate signup is rejected"""
        response = client.post(
            "/activities/Debate Club/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Fake Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_adds_to_participants(self, client, reset_activities):
        """Test that signup actually adds the participant"""
        from app import activities
        
        initial_count = len(activities["Go Club"]["participants"])
        client.post("/activities/Go Club/signup?email=newstudent@mergington.edu")
        final_count = len(activities["Go Club"]["participants"])
        
        assert final_count == initial_count + 1
        assert "newstudent@mergington.edu" in activities["Go Club"]["participants"]


class TestDeregister:
    """Tests for deregistering from activities"""
    
    def test_deregister_success(self, client, reset_activities):
        """Test successful deregistration"""
        response = client.post(
            "/activities/Debate Club/deregister?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Deregistered" in data["message"]
        assert "alex@mergington.edu" in data["message"]
    
    def test_deregister_not_signed_up(self, client, reset_activities):
        """Test deregister for student not signed up"""
        response = client.post(
            "/activities/Debate Club/deregister?email=notasignup@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_deregister_nonexistent_activity(self, client, reset_activities):
        """Test deregister from non-existent activity"""
        response = client.post(
            "/activities/Fake Club/deregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_deregister_removes_from_participants(self, client, reset_activities):
        """Test that deregister actually removes the participant"""
        from app import activities
        
        initial_count = len(activities["Debate Club"]["participants"])
        client.post("/activities/Debate Club/deregister?email=alex@mergington.edu")
        final_count = len(activities["Debate Club"]["participants"])
        
        assert final_count == initial_count - 1
        assert "alex@mergington.edu" not in activities["Debate Club"]["participants"]


class TestSignupAndDeregisterFlow:
    """Tests for combined signup and deregister flows"""
    
    def test_signup_then_deregister(self, client, reset_activities):
        """Test signing up and then deregistering"""
        email = "flow@mergington.edu"
        activity = "Chess Club"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signup worked
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity]["participants"]
        
        # Deregister
        deregister_response = client.post(
            f"/activities/{activity}/deregister?email={email}"
        )
        assert deregister_response.status_code == 200
        
        # Verify deregister worked
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity]["participants"]
