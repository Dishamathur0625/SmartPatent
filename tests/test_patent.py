from unittest.mock import patch, MagicMock
from services.prior_art_service import rank_patents_tfidf

def test_idor_unauthorized_download(client):
    # Test downloading without logging in redirect
    response = client.get("/download_draft/pdf/5")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

@patch("models.draft_model.DraftModel.get_draft_by_id")
def test_idor_wrong_user_blocks_access(mock_get_draft, client):
    # Mock database to return a draft owned by user 99
    mock_get_draft.return_value = {
        "id": 5,
        "user_id": 99,
        "title": "Confidential Draft",
        "draft_text": "Secret text"
    }
    
    # Simulate session as user 1
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Attacker User"
        
    response = client.get("/download_draft/txt/5")
    assert response.status_code == 403
    assert b"Forbidden" in response.data

@patch("models.draft_model.DraftModel.get_draft_by_id")
@patch("models.draft_model.DraftModel.update_draft_text")
def test_authorized_edit_allowed(mock_update, mock_get_draft, client):
    # Mock database to return a draft owned by user 1
    mock_get_draft.return_value = {
        "id": 5,
        "user_id": 1,
        "title": "My Draft",
        "draft_text": "Original text"
    }
    
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Owner User"
        
    response = client.post("/edit_draft/5", data={
        "draft_text": "New updated draft text content"
    })
    
    assert response.status_code == 200
    assert response.json["success"] is True
    mock_update.assert_called_once_with(5, "New updated draft text content", True)

def test_tfidf_math_ranking_accuracy():
    data = {
        "title": "Smart Food Spoilage Sensor",
        "field": "Internet of Things sensor systems",
        "problem": "Food goes bad in refrigerators without warning",
        "proposed_solution": "A system checking organic compound gas spikes and reporting it."
    }
    
    related = [
        {
            "patent_title": "Internet of Things Spoilage Detector for Fridge",
            "patent_number": "US101",
            "abstract_text": "This patent discusses detecting food spoilage by utilizing gas sensors inside a refrigerator."
        },
        {
            "patent_title": "Completely Unrelated Farming System",
            "patent_number": "US202",
            "abstract_text": "A method of watering corn fields using solar panels and automated tractors."
        }
    ]
    
    ranked = rank_patents_tfidf(data, related)
    
    assert len(ranked) == 2
    # The Spoilage detector should have a higher similarity than the farming system
    assert ranked[0]["patent_number"] == "US101"
    assert ranked[0]["similarity_percent"] > ranked[1]["similarity_percent"]
