"""Typed config-entry data and runtime state for DRIQON."""
from __future__ import annotations

from typing import TypedDict

from .api import Device


class DriqonConfigEntryData(TypedDict):
    """Non-password configuration data persisted by Home Assistant."""

    email: str
    firebase_api_key: str
    api_url: str
    refresh_token: str
    uid: str


DeviceMap = dict[str, Device]
