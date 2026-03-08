"""Tests for the Mergington High School Activities API using AAA pattern"""
import pytest


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static/index.html"""
        # Arrange
        expected_redirect_url = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect_url


class TestGetActivities:
    """Tests for getting activities"""

    def test_get_all_activities(self, client, reset_activities):
        """Test that all activities are returned"""
        # Arrange
        expected_activity_names = ["Chess Club", "Programming Class", "Gym Class",
                                   "Tennis Club", "Basketball Team", "Drama Club",
                                   "Art Studio", "Debate Team", "Science Club"]

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert len(data) == 9
        for activity_name in expected_activity_names:
            assert activity_name in data

    def test_activity_has_required_fields(self, client, reset_activities):
        """Test that each activity has required fields"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Missing {field} in {activity_name}"


class TestSignupForActivity:
    """Tests for signing up for an activity"""

    def test_successful_signup(self, client, reset_activities):
        """Test successful signup for an activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "newemail@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

        # Verify participant was added
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]

    def test_signup_duplicate_fails(self, client, reset_activities):
        """Test that duplicate signup fails"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Test that signup for non-existent activity fails"""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_at_max_capacity_fails(self, client, reset_activities):
        """Test that signup fails when activity at max capacity"""
        # Arrange - manually fill activity to capacity
        from app import activities
        activity_name = "Tennis Club"
        activity = activities[activity_name]

        # Fill to capacity
        while len(activity["participants"]) < activity["max_participants"]:
            activity["participants"].append(f"filler{len(activity['participants'])}@test.edu")

        new_email = "newstudent@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={new_email}")

        # Assert
        assert response.status_code == 400
        assert "max capacity" in response.json()["detail"]


class TestRemoveParticipant:
    """Tests for removing a participant from an activity"""

    def test_successful_removal(self, client, reset_activities):
        """Test successful removal of a participant"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]

        # Verify participant was removed
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity_name]["participants"]

    def test_remove_nonexistent_activity_fails(self, client, reset_activities):
        """Test that removing from non-existent activity fails"""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_remove_nonexistent_participant_fails(self, client, reset_activities):
        """Test that removing non-existent participant fails"""
        # Arrange
        activity_name = "Drama Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert
        assert response.status_code == 404
        assert "not signed up" in response.json()["detail"]