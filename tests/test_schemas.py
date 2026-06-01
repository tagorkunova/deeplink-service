import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models.schemas import DeepLinkCreate
from pydantic import ValidationError


def test_valid_deeplink_create():
    data = DeepLinkCreate(
        targetUrl="https://example.com/promo",
        ttlSeconds=3600,
        payload={"userId": "123"},
    )
    assert data.targetUrl == "https://example.com/promo"
    assert data.ttlSeconds == 3600
    assert data.payload == {"userId": "123"}


def test_invalid_url_rejected():
    with pytest.raises(ValidationError) as exc_info:
        DeepLinkCreate(targetUrl="not-a-url", ttlSeconds=3600)
    assert "http" in str(exc_info.value).lower() or "url" in str(exc_info.value).lower()


def test_url_without_scheme_rejected():
    with pytest.raises(ValidationError):
        DeepLinkCreate(targetUrl="example.com/promo", ttlSeconds=3600)


def test_negative_ttl_rejected():
    with pytest.raises(ValidationError):
        DeepLinkCreate(targetUrl="https://example.com", ttlSeconds=-1)


def test_zero_ttl_rejected():
    with pytest.raises(ValidationError):
        DeepLinkCreate(targetUrl="https://example.com", ttlSeconds=0)


def test_ttl_exceeds_max_rejected():
    with pytest.raises(ValidationError):
        DeepLinkCreate(targetUrl="https://example.com", ttlSeconds=86400 * 366)


def test_default_payload_is_empty_dict():
    data = DeepLinkCreate(targetUrl="https://example.com", ttlSeconds=100)
    assert data.payload == {}


def test_http_url_accepted():
    data = DeepLinkCreate(targetUrl="http://localhost:3000/test", ttlSeconds=60)
    assert data.targetUrl.startswith("http://")


def test_https_url_accepted():
    data = DeepLinkCreate(targetUrl="https://google.com", ttlSeconds=3600)
    assert data.targetUrl.startswith("https://")


def test_payload_with_multiple_fields():
    data = DeepLinkCreate(
        targetUrl="https://example.com",
        ttlSeconds=3600,
        payload={"userId": "42", "campaign": "sale", "source": "email"},
    )
    assert data.payload["userId"] == "42"
    assert data.payload["campaign"] == "sale"
    assert data.payload["source"] == "email"


def test_default_ttl_is_one_hour():
    data = DeepLinkCreate(targetUrl="https://example.com")
    assert data.ttlSeconds == 3600
