"""What the audit of 0.10.8 found in the take-over and in what follows a discovery.

The harness runs a Home Assistant older than 2026.11, where an entity
taken over is given its whole shown name. From 2026.11 one without a
name of its own is given none; the tests of that case make the name
carried the one 2026.11 gives, and say so.
"""

from __future__ import annotations

from typing import Any

import pytest
from homeassistant.config_entries import ConfigEntryDisabler, ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nikobus_ng.const import DATA_LINKS_TRIED, DOMAIN

from .conftest import ENTRY_ID, ROLLER, SWITCH, SetupFixture
from .test_ai import _nikobus_entities
from .test_remaining import GROUP, _options, _reloaded, _stored


def _a_shutter_group(hass_storage: dict[str, Any]) -> None:
    _stored(hass_storage)["scenes"] = {
        GROUP: {
            "bus_address": GROUP,
            "pattern": "roller_pair",
            "outputs": [
                {"module_address": ROLLER, "channel": channel, "mode": "M01 (Open - stop - close)", "t1": "30s"}
                for channel in (1, 2)
            ],
        }
    }


async def test_an_entity_without_a_name_of_its_own_is_taken_over_with_its_area_on_the_device(
    hass: HomeAssistant, hass_storage: dict[str, Any], setup: SetupFixture, entry: MockConfigEntry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A shutter group stands for its device: the registry refuses it an area of its own.

    The name carried is forced to none, as Home Assistant 2026.11 gives it.
    """
    monkeypatch.setattr("custom_components.nikobus_ng.takeover._carried_name", lambda *_: None)
    _a_shutter_group(hass_storage)
    old = MockConfigEntry(domain="nikobus", title="Nikobus", disabled_by=ConfigEntryDisabler.USER)
    old.add_to_hass(hass)
    registry = er.async_get(hass)
    area = ar.async_get(hass).async_create("Living")
    there = registry.async_get_or_create(
        "cover", "nikobus", f"nikobus_cf_cover_{GROUP}", config_entry=old, suggested_object_id="all_shutters"
    )
    registry.async_update_entity(there.entity_id, area_id=area.id)
    hub = await setup()
    result = await _options(hass, entry, {"next_step_id": "take_over"}, {})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    taken = await _reloaded(hass, entry, hub)

    assert entry.state is ConfigEntryState.LOADED
    mine = registry.async_get("cover.all_shutters")
    assert (mine.platform, mine.unique_id, mine.area_id) == (DOMAIN, f"{GROUP}_group", None)
    assert dr.async_get(hass).async_get(mine.device_id).area_id == area.id
    assert [item["entity_id"] for item in taken.inventory.takeover["done"]] == ["cover.all_shutters"]


async def test_an_id_the_registry_refuses_does_not_lose_the_rest_of_a_take_over(
    hass: HomeAssistant, setup: SetupFixture, entry: MockConfigEntry
) -> None:
    _nikobus_entities(hass)
    hub = await setup()
    # The id the Nikobus light would be parked under is in use: the registry refuses it.
    hass.states.async_set("light.kitchen_ceiling_nikobus", "on")
    result = await _options(hass, entry, {"next_step_id": "take_over"}, {})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    taken = await _reloaded(hass, entry, hub)

    assert entry.state is ConfigEntryState.LOADED
    registry = er.async_get(hass)
    assert registry.async_get("light.kitchen_ceiling").platform == "nikobus"
    assert registry.async_get("light.living_spots").platform == DOMAIN
    done = {item["entity_id"] for item in taken.inventory.takeover["done"]}
    assert "light.living_spots" in done
    assert "light.kitchen_ceiling" not in done


async def test_an_entity_with_no_counterpart_here_is_not_counted_as_one_to_take(
    hass: HomeAssistant, setup: SetupFixture, entry: MockConfigEntry
) -> None:
    old = _nikobus_entities(hass)
    er.async_get(hass).async_get_or_create(
        "binary_sensor", "nikobus", "nikobus_button_ABCDEF", config_entry=old, suggested_object_id="a_key_not_here"
    )
    await setup()
    result = await _options(hass, entry, {"next_step_id": "take_over"})
    placeholders = result["description_placeholders"]
    assert (placeholders["entities"], placeholders["left"]) == ("5", "2")
    hass.config_entries.options.async_abort(result["flow_id"])


async def test_removing_the_entry_gives_back_what_it_took(
    hass: HomeAssistant, setup: SetupFixture, entry: MockConfigEntry
) -> None:
    _nikobus_entities(hass)
    hub = await setup()
    await _options(hass, entry, {"next_step_id": "take_over"}, {})
    await _reloaded(hass, entry, hub)
    registry = er.async_get(hass)
    assert registry.async_get("light.kitchen_ceiling").platform == DOMAIN

    assert await hass.config_entries.async_remove(entry.entry_id)
    await hass.async_block_till_done()
    assert registry.async_get("light.kitchen_ceiling").platform == "nikobus"
    assert registry.async_get("light.kitchen_ceiling_nikobus") is None


async def test_links_that_could_not_be_read_are_not_looked_for_at_every_setup(
    hass: HomeAssistant, hass_storage: dict[str, Any], setup: SetupFixture, entry: MockConfigEntry
) -> None:
    """An inventory from a project file whose modules gave no links: each discovery ends in a reload.

    The discovery that found none is the state made here; the next test shows a discovery leaving it.
    """
    _stored(hass_storage)["from_project"] = True
    hass.data[DATA_LINKS_TRIED] = {ENTRY_ID}
    hub = await setup()
    assert not hub.inventory.links_read(SWITCH)
    assert not hub.discovery.running


async def test_a_full_discovery_is_remembered_until_home_assistant_restarts(
    hass: HomeAssistant, scanned: SetupFixture
) -> None:
    await scanned()
    assert ENTRY_ID in hass.data[DATA_LINKS_TRIED]


async def test_a_shutter_group_follows_a_member_that_changes_its_entity_id(
    hass: HomeAssistant, hass_storage: dict[str, Any], setup: SetupFixture
) -> None:
    _a_shutter_group(hass_storage)
    await setup()
    registry = er.async_get(hass)
    group = registry.async_get_entity_id("cover", DOMAIN, f"{GROUP}_group")
    first = registry.async_get_entity_id("cover", DOMAIN, f"{ROLLER}_1")
    registry.async_update_entity(first, new_entity_id="cover.living_left")
    await hass.async_block_till_done()
    assert hass.states.get(group).attributes["entity_id"][0] == "cover.living_left"


async def test_a_module_the_options_call_a_dimmer_is_never_written_without_a_read(
    hass: HomeAssistant, scanned: SetupFixture
) -> None:
    hub = await scanned()
    inventory = hub.inventory
    assert (SWITCH, 1) in inventory.steady_groups()
    inventory.module_types[SWITCH] = "dimmer_module"
    inventory.changed()
    assert not {key for key in inventory.steady_groups() if key[0] == SWITCH}
