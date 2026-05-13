import pytest
from unittest.mock import patch
from app.errors import Unauthenticated, Forbidden


def test_require_user_no_session():
    from app.auth.guards import require_user
    with patch("app.auth.guards.session", {}):
        with pytest.raises(Unauthenticated):
            require_user()


def test_require_user_with_session():
    from app.auth.guards import require_user
    mock_user = {"_id": "123", "email": "a@chula.ac.th", "role": "user"}
    with patch("app.auth.guards.session", {"user_id": "123"}):
        with patch("app.auth.guards.get_db") as mock_db:
            mock_db().users.find_one.return_value = mock_user
            user = require_user()
            assert user["email"] == "a@chula.ac.th"


def test_require_web_admin_wrong_role():
    from app.auth.guards import require_web_admin
    mock_user = {"_id": "123", "role": "location_admin"}
    with patch("app.auth.guards.require_user", return_value=mock_user):
        with pytest.raises(Forbidden):
            require_web_admin()


def test_require_web_admin_correct_role():
    from app.auth.guards import require_web_admin
    mock_user = {"_id": "123", "role": "web_admin"}
    with patch("app.auth.guards.require_user", return_value=mock_user):
        user = require_web_admin()
        assert user["role"] == "web_admin"


def test_require_any_admin_web_admin():
    from app.auth.guards import require_any_admin
    mock_user = {"_id": "123", "role": "web_admin"}
    with patch("app.auth.guards.require_user", return_value=mock_user):
        user = require_any_admin()
        assert user is not None


def test_require_any_admin_location_admin():
    from app.auth.guards import require_any_admin
    mock_user = {"_id": "123", "role": "location_admin"}
    with patch("app.auth.guards.require_user", return_value=mock_user):
        user = require_any_admin()
        assert user is not None


def test_require_any_admin_forbidden():
    from app.auth.guards import require_any_admin
    mock_user = {"_id": "123", "role": "user"}
    with patch("app.auth.guards.require_user", return_value=mock_user):
        with pytest.raises(Forbidden):
            require_any_admin()