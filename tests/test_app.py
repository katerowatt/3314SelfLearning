import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities dictionary before each test to ensure isolation."""
    # Store the original activities data
    original_activities = {
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
        },
        "Basketball Team": {
            "description": "Practice and compete in basketball games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Soccer Club": {
            "description": "Train and play soccer matches",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 5:00 PM",
            "max_participants": 22,
            "participants": []
        },
        "Art Club": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": []
        },
        "Drama Club": {
            "description": "Act in plays and learn theater skills",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": []
        },
        "Debate Club": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": []
        },
        "Science Club": {
            "description": "Conduct experiments and learn about scientific concepts",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": []
        }
    }
    
    # Reset activities to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test (optional, as we reset before each test)


def test_get_activities(client):
    """Test GET /activities endpoint returns all activities."""
    # Arrange: No special setup needed, activities are reset by fixture
    
    # Act: Make GET request to /activities
    response = client.get("/activities")
    
    # Assert: Check status code and response data
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # Should have 9 activities
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Verify structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert chess_club["max_participants"] == 12
    assert len(chess_club["participants"]) == 2


def test_signup_success(client):
    """Test successful signup for an activity."""
    # Arrange: Use an activity with available spots
    activity_name = "Basketball Team"
    email = "newstudent@mergington.edu"
    
    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert: Check success response
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Signed up {email} for {activity_name}" in data["message"]
    
    # Verify participant was added
    get_response = client.get("/activities")
    activities_data = get_response.json()
    assert email in activities_data[activity_name]["participants"]


def test_signup_duplicate(client):
    """Test that duplicate signup is prevented."""
    # Arrange: Sign up once first
    activity_name = "Basketball Team"
    email = "teststudent@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Act: Try to sign up again
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert: Should get 400 error
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()


def test_signup_invalid_activity(client):
    """Test signup for non-existent activity returns 404."""
    # Arrange: Use invalid activity name
    invalid_activity = "NonExistent Club"
    email = "student@mergington.edu"
    
    # Act: Make POST request
    response = client.post(f"/activities/{invalid_activity}/signup?email={email}")
    
    # Assert: Should get 404 error
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_unregister_success(client):
    """Test successful unregister from an activity."""
    # Arrange: First sign up a student
    activity_name = "Basketball Team"
    email = "removeme@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Act: Unregister the student
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    
    # Assert: Check success response
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Unregistered {email} from {activity_name}" in data["message"]
    
    # Verify participant was removed
    get_response = client.get("/activities")
    activities_data = get_response.json()
    assert email not in activities_data[activity_name]["participants"]


def test_unregister_not_registered(client):
    """Test unregister for student not in activity returns 400."""
    # Arrange: Use activity and email where student is not registered
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"
    
    # Act: Try to unregister
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    
    # Assert: Should get 400 error
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not registered" in data["detail"].lower()


def test_unregister_invalid_activity(client):
    """Test unregister for non-existent activity returns 404."""
    # Arrange: Use invalid activity name
    invalid_activity = "Fake Club"
    email = "student@mergington.edu"
    
    # Act: Make DELETE request
    response = client.delete(f"/activities/{invalid_activity}/unregister?email={email}")
    
    # Assert: Should get 404 error
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()