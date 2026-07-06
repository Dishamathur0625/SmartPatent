from unittest.mock import patch, MagicMock
from werkzeug.security import generate_password_hash

def test_signup_validation(client):
    # Test short password
    response = client.post("/signup", data={
        "name": "Test User",
        "email": "test@domain.com",
        "password": "123"
    })
    assert b"Password must be at least 8 characters long." in response.data

    # Test invalid email format
    response = client.post("/signup", data={
        "name": "Test User",
        "email": "invalidemail",
        "password": "password123"
    })
    assert b"Please enter a valid email address." in response.data

@patch("models.user_model.UserModel.get_user_by_email")
def test_signup_duplicate_email(mock_get_user, client):
    # Mock that email already exists
    mock_get_user.return_value = {"user_id": 1, "email": "exists@domain.com"}
    
    response = client.post("/signup", data={
        "name": "Test User",
        "email": "exists@domain.com",
        "password": "password123"
    })
    assert b"Email is already registered." in response.data

@patch("models.user_model.UserModel.get_user_by_email")
@patch("models.user_model.UserModel.create_user")
def test_signup_success(mock_create, mock_get_user, client):
    # Mock email is unique
    mock_get_user.return_value = None
    
    response = client.post("/signup", data={
        "name": "Test User",
        "email": "new@domain.com",
        "password": "password123"
    })
    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

@patch("models.user_model.UserModel.get_user_by_email")
def test_login_failed(mock_get_user, client):
    mock_get_user.return_value = None
    response = client.post("/login", data={
        "email": "wrong@domain.com",
        "password": "password123"
    })
    assert b"Invalid email or password." in response.data

@patch("models.user_model.UserModel.get_user_by_email")
def test_login_success(mock_get_user, client):
    hashed = generate_password_hash("password123")
    mock_get_user.return_value = {
        "user_id": 1,
        "name": "Authorized User",
        "email": "correct@domain.com",
        "password": hashed
    }
    
    response = client.post("/login", data={
        "email": "correct@domain.com",
        "password": "password123"
    })
    assert response.status_code == 302
    assert response.headers["Location"] == "/dashboard"

@patch("models.user_model.UserModel.get_user_by_email")
@patch("models.user_model.UserModel.set_password_reset_token")
def test_forgot_password(mock_set_token, mock_get_user, client):
    # Mock email registration
    mock_get_user.return_value = {"user_id": 1, "email": "user@domain.com"}
    
    response = client.post("/forgot_password", data={
        "email": "user@domain.com"
    })
    
    assert response.status_code == 200
    assert b"logged to the server console" in response.data
    mock_set_token.assert_called_once()

@patch("models.user_model.UserModel.get_user_by_reset_token")
@patch("models.user_model.UserModel.update_password")
@patch("models.user_model.UserModel.clear_password_reset_token")
def test_reset_password(mock_clear_token, mock_update, mock_get_token, client):
    # Mock valid reset token
    mock_get_token.return_value = {"user_id": 1, "email": "user@domain.com"}
    
    response = client.post("/reset_password/test_token", data={
        "password": "newpassword123"
    })
    
    assert response.status_code == 200
    assert b"Password reset successful" in response.data
    mock_update.assert_called_once()
    mock_clear_token.assert_called_once_with(1)
