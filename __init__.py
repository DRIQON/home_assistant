"""DRIQON cloud integration setup and config-entry lifecycle."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DriqonApi, DriqonApiError
from .const import CONF_API_KEY, CONF_API_URL, DOMAIN, PLATFORMS
from .coordinator import DriqonCoordinator
from .types import DriqonConfigEntryData


@dataclass
class DriqonRuntimeData:
    """Resources owned by one configured DRIQON account."""

    api: DriqonApi
    coordinator: DriqonCoordinator


type DriqonConfigEntry = ConfigEntry[DriqonRuntimeData]


async def async_setup(hass: HomeAssistant, config: dict[str, object]) -> bool:
    """Register packaged DRIQON images for the frontend."""
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                "/api/driqon/images",
                str(Path(__file__).parent / "static"),
                True,
            )
        ]
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: DriqonConfigEntry) -> bool:
    """Set up an authenticated DRIQON account."""
    api = DriqonApi(
        async_get_clientsession(hass),
        entry.data["email"],
        api_key=entry.data[CONF_API_KEY],
        api_url=entry.data[CONF_API_URL],
        refresh_token=entry.data["refresh_token"],
    )
    coordinator = DriqonCoordinator(hass, api, entry)
    try:
        await coordinator.async_config_entry_first_refresh()
    except DriqonApiError as err:
        raise ConfigEntryNotReady("Could not connect to DRIQON") from err
    entry.runtime_data = DriqonRuntimeData(api=api, coordinator=coordinator)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: DriqonConfigEntry) -> bool:
    """Unload all platform entities for an account."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
