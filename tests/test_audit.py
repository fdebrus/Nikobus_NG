"""What the audit of 0.10.8 found, one test a finding.

The simulator has no checksum function, so the checksum a module
reports is given here, as in ``test_maintenance``. Where a test puts
the library or the registry in a state the simulator cannot produce (a
command cut off by a dropped line), it says so.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
import voluptuous as vol
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import issue_registry as ir
from nikobus_connect import NikobusAPI
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nikobus_ng import async_remove_config_entry_device
from custom_components.nikobus_ng.const import (
    CONF_OLD_PC_LINK,
    CONF_PRESS_REPEAT,
    DOMAIN,
)
from custom_components.nikobus_ng.diagnostics import async_get_config_entry_diagnostics

from .conftest import (
    DIMMER,
    KEY_ROLLER,
    KEY_SWITCH_1,
    ROLLER,
    SWITCH,
    SetupFixture,
    WallSimulator,
    wait_for,
)
from .test_ai import _tool
from .test_remaining import _options, _reloaded


async def test_a_stop_on_a_shutter_at_rest_presses_no_key(
    hass: HomeAssistant, simulator: WallSimulator, setup: SetupFixture, entry: MockConfigEntry
) -> None:
    hub = await setup()
    await _options(
        hass, entry, {"next_step_id": "led_key"}, {"output": f"{ROLLER}:1"}, {"on_key": KEY_ROLLER, "off_key": KEY_ROLLER}
    )
    await _reloaded(hass, entry, hub)
    cover = er.async_get(hass).async_get_entity_id("cover", DOMAIN, f"{ROLLER}_1")
    await hass.services.async_call("cover", "stop_cover", {"entity_id": cover}, blocking=True)
    # The key that stops a move would have started one.
    assert simulator.host_presses == []
    assert simulator.output(ROLLER, 1) == 0x00


async def test_a_dimmer_is_switched_on_at_the_level_it_last_had(
    hass: HomeAssistant, simulator: WallSimulator, setup: SetupFixture
) -> None:
    await setup()
    light = er.async_get(hass).async_get_entity_id("light", DOMAIN, f"{DIMMER}_1")
    await hass.services.async_call("light", "turn_on", {"entity_id": light, "brightness": 77}, blocking=True)
    await hass.services.async_call("light", "turn_off", {"entity_id": light}, blocking=True)
    assert simulator.output(DIMMER, 1) == 0
    await hass.services.async_call("light", "turn_on", {"entity_id": light}, blocking=True)
    assert simulator.output(DIMMER, 1) == 77


async def test_the_press_tool_refuses_an_address_that_is_no_key(
    hass: HomeAssistant, simulator: WallSimulator, setup: SetupFixture
) -> None:
    await setup()
    with pytest.raises(HomeAssistantError):
        await _tool(hass, "nikobus_press_key", address="ABCDEF")
    await asyncio.sleep(0.1)
    assert simulator.host_presses == []


async def test_an_address_followed_by_a_line_feed_is_no_address(hass: HomeAssistant, setup: SetupFixture) -> None:
    await setup()
    with pytest.raises(vol.Invalid):
        await hass.services.async_call(DOMAIN, "press_key", {"address": f"{KEY_SWITCH_1}\n"}, blocking=True)


async def test_an_entry_that_is_not_loaded_still_answers(hass: HomeAssistant) -> None:
    """An entry that never connected has no hub."""
    entry = MockConfigEntry(domain=DOMAIN, data={"connection": "nowhere:1", "feedback_module": False})
    entry.add_to_hass(hass)
    device = dr.async_get(hass).async_get_or_create(config_entry_id=entry.entry_id, identifiers={(DOMAIN, SWITCH)})
    assert await async_remove_config_entry_device(hass, entry, device) is False
    diagnostics = await async_get_config_entry_diagnostics(hass, entry)
    assert diagnostics["state"] == ConfigEntryState.NOT_LOADED.value
    assert "nowhere" not in str(diagnostics)


async def test_forgetting_a_module_withdraws_every_repair_about_it(hass: HomeAssistant, setup: SetupFixture) -> None:
    hub = await setup()
    issues = ir.async_get(hass)
    for key in ("module_reprogrammed", "module_checksum_mismatch", "module_corrupt_links"):
        ir.async_create_issue(
            hass, DOMAIN, f"{key}_{SWITCH.lower()}", is_fixable=False, severity=ir.IssueSeverity.WARNING,
            translation_key=key, translation_placeholders={"module": SWITCH},
        )
    await hub.async_forget(SWITCH)
    assert [issue for issue in issues.issues if issue[0] == DOMAIN] == []


@pytest.mark.usefixtures("quick_timeouts")
async def test_a_backup_of_modules_that_stay_silent_is_an_error(
    hass: HomeAssistant, simulator: WallSimulator, setup: SetupFixture, tmp_path: Path
) -> None:
    hass.config.config_dir = str(tmp_path)
    await setup()
    simulator.gateway.modules.pop(SWITCH)
    with pytest.raises(HomeAssistantError) as raised:
        await hass.services.async_call(
            DOMAIN, "backup_programming", {"modules": [SWITCH]}, blocking=True, return_response=True
        )
    assert raised.value.translation_key == "backup_nothing_read"
    assert not (tmp_path / "nikobus_ng_backup").exists()


@pytest.mark.usefixtures("quick_timeouts")
async def test_reading_a_module_that_stays_silent_is_an_error(
    hass: HomeAssistant, simulator: WallSimulator, setup: SetupFixture
) -> None:
    await setup()
    simulator.gateway.modules.pop(ROLLER)
    with pytest.raises(HomeAssistantError) as raised:
        await hass.services.async_call(DOMAIN, "read_module", {"address": ROLLER}, blocking=True)
    assert raised.value.translation_key == "module_did_not_answer"


async def test_a_check_does_not_settle_a_module_that_was_reprogrammed(hass: HomeAssistant, setup: SetupFixture) -> None:
    hub = await setup()
    with patch.object(NikobusAPI, "get_module_crc", AsyncMock(return_value=0x1234)):
        report = await hass.services.async_call(
            DOMAIN, "verify_programming", {"modules": [SWITCH]}, blocking=True, return_response=True
        )
    now: int = report["modules"][SWITCH]["computed_checksum"]
    kept = {"checksum": now ^ 0x0101, "recorded_at": "2026-11-01T00:00:00+00:00", "volatile": {}}
    hub.inventory.programming[SWITCH] = dict(kept)
    with patch.object(NikobusAPI, "get_module_crc", AsyncMock(return_value=now)):
        await hass.services.async_call(
            DOMAIN, "verify_programming", {"modules": [SWITCH]}, blocking=True, return_response=True
        )
    # The memory is sound, but it is not the one whose links were read.
    assert hub.inventory.programming[SWITCH] == kept


async def test_a_command_cut_off_by_a_dropped_line_is_a_failed_command(hass: HomeAssistant, setup: SetupFixture) -> None:
    """The library cancels the answer a command waits for when the line drops; that state is made here."""
    hub = await setup()
    answer: asyncio.Future[Any] = hass.loop.create_future()
    answer.cancel()
    switch = er.async_get(hass).async_get_entity_id("switch", DOMAIN, f"{SWITCH}_3")
    with (
        patch.object(hub.command, "set_output_state", AsyncMock(return_value=answer)),
        pytest.raises(HomeAssistantError) as raised,
    ):
        await hass.services.async_call("switch", "turn_on", {"entity_id": switch}, blocking=True)
    assert raised.value.translation_key == "command_failed"
    await hass.async_block_till_done()


async def test_an_old_pc_link_is_asked_for_no_state(hass: HomeAssistant, setup: SetupFixture, entry: MockConfigEntry) -> None:
    hub = await setup()
    await _options(
        hass, entry, {"next_step_id": "gateway"}, {"feedback_module": False, CONF_OLD_PC_LINK: True, CONF_PRESS_REPEAT: 3}
    )
    await hass.async_block_till_done()
    await wait_for(lambda: entry.runtime_data is not hub and entry.state is ConfigEntryState.LOADED)
    old = entry.runtime_data
    with patch.object(old.command, "get_output_state", AsyncMock()) as asked:
        assert await old.async_read_group(SWITCH, 1) is False
    asked.assert_not_awaited()
