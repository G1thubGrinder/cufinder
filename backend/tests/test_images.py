import pytest
from io import BytesIO


def test_upload_wrong_mime(client):
    data = {"file": (BytesIO(b"fake content"), "test.txt")}
    res = client.post("/api/images", data=data, content_type="multipart/form-data")
    assert res.status_code == 400


def test_upload_too_large(client):
    big = BytesIO(b"x" * (5 * 1024 * 1024 + 1))
    data = {"file": (big, "big.jpg")}
    res = client.post("/api/images", data=data, content_type="multipart/form-data")
    assert res.status_code == 400


def test_upload_no_file(client):
    res = client.post("/api/images", data={}, content_type="multipart/form-data")
    assert res.status_code == 400


def test_upload_no_extension(client):
    data = {"file": (BytesIO(b"fake"), "noextension")}
    res = client.post("/api/images", data=data, content_type="multipart/form-data")
    assert res.status_code == 400