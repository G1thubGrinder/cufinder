import pytest


def build_filter(status=None, type=None, location_id=None, search=None):
    f = {}
    if status:
        f["status"] = status
    if type:
        f["type"] = type
    if location_id:
        f["last_seen_location_id"] = location_id
    if search:
        f["title"] = {"$regex": search, "$options": "i"}
    return f


def test_default_filter():
    f = build_filter()
    assert f == {}


def test_status_filter():
    f = build_filter(status="open")
    assert f["status"] == "open"


def test_type_filter():
    f = build_filter(type="lost")
    assert f["type"] == "lost"


def test_search_filter():
    f = build_filter(search="wallet")
    assert "$regex" in f["title"]


def test_location_filter():
    f = build_filter(location_id="abc123")
    assert f["last_seen_location_id"] == "abc123"