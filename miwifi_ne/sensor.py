"""Sensor component."""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Final

from homeassistant.components.sensor import (
    ENTITY_ID_FORMAT,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfInformation, UnitOfTemperature, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ATTR_SENSOR_AP_SIGNAL,
    ATTR_SENSOR_AP_SIGNAL_NAME,
    ATTR_SENSOR_CONNECTIONS_SUMMARY,
    ATTR_SENSOR_DEVICES,
    ATTR_SENSOR_DEVICES_2_4,
    ATTR_SENSOR_DEVICES_2_4_NAME,
    ATTR_SENSOR_DEVICES_5_0,
    ATTR_SENSOR_DEVICES_5_0_GAME,
    ATTR_SENSOR_DEVICES_5_0_GAME_NAME,
    ATTR_SENSOR_DEVICES_5_0_NAME,
    ATTR_SENSOR_DEVICES_GUEST,
    ATTR_SENSOR_DEVICES_GUEST_NAME,
    ATTR_SENSOR_DEVICES_LAN,
    ATTR_SENSOR_DEVICES_LAN_NAME,
    ATTR_SENSOR_DEVICES_NAME,
    ATTR_SENSOR_MEMORY_TOTAL,
    ATTR_SENSOR_MEMORY_TOTAL_NAME,
    ATTR_SENSOR_MEMORY_USAGE,
    ATTR_SENSOR_MEMORY_USAGE_NAME,
    ATTR_SENSOR_MODE,
    ATTR_SENSOR_MODE_NAME,
    ATTR_SENSOR_TEMPERATURE,
    ATTR_SENSOR_TEMPERATURE_NAME,
    ATTR_SENSOR_UPTIME,
    ATTR_SENSOR_UPTIME_NAME,
    ATTR_SENSOR_VPN_UPTIME,
    ATTR_SENSOR_VPN_UPTIME_NAME,
    ATTR_SENSOR_WAN_DOWNLOAD_SPEED,
    ATTR_SENSOR_WAN_DOWNLOAD_SPEED_NAME,
    ATTR_SENSOR_WAN_UPLOAD_SPEED,
    ATTR_SENSOR_WAN_UPLOAD_SPEED_NAME,
    ATTR_STATE,
    ATTR_TRACKER_CONNECTION,
    ATTR_TRACKER_DOWN_SPEED,
    ATTR_TRACKER_IP,
    ATTR_TRACKER_MAC,
    ATTR_TRACKER_NAME,
    ATTR_TRACKER_ONLINE,
    ATTR_TRACKER_SIGNAL,
    ATTR_TRACKER_UP_SPEED,
)
from .entity import MiWifiEntity
from .enum import Connection, DeviceClass
from .updater import LuciUpdater, async_get_updater

PARALLEL_UPDATES = 0

DISABLE_ZERO: Final = (
    ATTR_SENSOR_TEMPERATURE,
    ATTR_SENSOR_AP_SIGNAL,
)

ONLY_WAN: Final = (
    ATTR_SENSOR_WAN_DOWNLOAD_SPEED,
    ATTR_SENSOR_WAN_UPLOAD_SPEED,
)

PCS: Final = "pcs"
BS: Final = "B/s"

MIWIFI_SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key=ATTR_SENSOR_UPTIME,
        name=ATTR_SENSOR_UPTIME_NAME,
        icon="mdi:timer-sand",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_VPN_UPTIME,
        name=ATTR_SENSOR_VPN_UPTIME_NAME,
        icon="mdi:timer-sand",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_MEMORY_USAGE,
        name=ATTR_SENSOR_MEMORY_USAGE_NAME,
        icon="mdi:memory",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_MEMORY_TOTAL,
        name=ATTR_SENSOR_MEMORY_TOTAL_NAME,
        icon="mdi:memory",
        native_unit_of_measurement=UnitOfInformation.MEGABYTES,
        state_class=SensorStateClass.TOTAL,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_TEMPERATURE,
        name=ATTR_SENSOR_TEMPERATURE_NAME,
        icon="mdi:temperature-celsius",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_MODE,
        name=ATTR_SENSOR_MODE_NAME,
        icon="mdi:transit-connection-variant",
        device_class=DeviceClass.MODE,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_AP_SIGNAL,
        name=ATTR_SENSOR_AP_SIGNAL_NAME,
        icon="mdi:wifi-arrow-left-right",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_WAN_DOWNLOAD_SPEED,
        name=ATTR_SENSOR_WAN_DOWNLOAD_SPEED_NAME,
        icon="mdi:speedometer",
        native_unit_of_measurement=BS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_WAN_UPLOAD_SPEED,
        name=ATTR_SENSOR_WAN_UPLOAD_SPEED_NAME,
        icon="mdi:speedometer",
        native_unit_of_measurement=BS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_DEVICES,
        name=ATTR_SENSOR_DEVICES_NAME,
        icon="mdi:counter",
        native_unit_of_measurement=PCS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_DEVICES_LAN,
        name=ATTR_SENSOR_DEVICES_LAN_NAME,
        icon="mdi:counter",
        native_unit_of_measurement=PCS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_DEVICES_2_4,
        name=ATTR_SENSOR_DEVICES_2_4_NAME,
        icon="mdi:counter",
        native_unit_of_measurement=PCS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_DEVICES_5_0,
        name=ATTR_SENSOR_DEVICES_5_0_NAME,
        icon="mdi:counter",
        native_unit_of_measurement=PCS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_DEVICES_GUEST,
        name=ATTR_SENSOR_DEVICES_GUEST_NAME,
        icon="mdi:counter",
        native_unit_of_measurement=PCS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key=ATTR_SENSOR_DEVICES_5_0_GAME,
        name=ATTR_SENSOR_DEVICES_5_0_GAME_NAME,
        icon="mdi:counter",
        native_unit_of_measurement=PCS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
)

CONNECTIONS_SUMMARY_DESCRIPTION = SensorEntityDescription(
    key=ATTR_SENSOR_CONNECTIONS_SUMMARY,
    translation_key="connections_summary",
    name=None,
    has_entity_name=True,
    icon="mdi:account-network",
    native_unit_of_measurement=PCS,
    state_class=SensorStateClass.MEASUREMENT,
    entity_registry_enabled_default=True,
)

_LOGGER = logging.getLogger(__name__)

_MAX_CLIENT_ROWS: Final = 48


def _connection_label(connection: Any) -> str:
    """Human-readable connection type for summary."""

    if isinstance(connection, Connection):
        return str(connection.phrase)

    if connection is None:
        return "—"

    return str(connection)


def _build_connections_summary(updater: LuciUpdater) -> tuple[int, dict[str, Any]]:
    """Build state value and attributes for the connections summary sensor."""

    devices: dict[str, dict[str, Any]] = updater.devices
    total: int = len(devices)

    by_type: dict[str, int] = {}
    rows: list[dict[str, Any]] = []

    known_phrases: set[str] = {
        Connection.LAN.phrase,
        Connection.WIFI_2_4.phrase,
        Connection.WIFI_5_0.phrase,
        Connection.WIFI_5_0_GAME.phrase,
        Connection.GUEST.phrase,
    }

    for mac, dev in devices.items():
        label = _connection_label(dev.get(ATTR_TRACKER_CONNECTION))
        by_type[label] = by_type.get(label, 0) + 1

        rows.append(
            {
                "name": dev.get(ATTR_TRACKER_NAME, mac),
                "ip": dev.get(ATTR_TRACKER_IP),
                "mac": mac,
                "connection": label,
                "signal": dev.get(ATTR_TRACKER_SIGNAL),
                "session_time": dev.get(ATTR_TRACKER_ONLINE),
                "download_mbps": round(float(dev.get(ATTR_TRACKER_DOWN_SPEED, 0.0) or 0.0), 2),
                "upload_mbps": round(float(dev.get(ATTR_TRACKER_UP_SPEED, 0.0) or 0.0), 2),
            }
        )

    rows.sort(key=lambda r: str(r.get("name") or "").lower())

    other: int = sum(
        count for phrase, count in by_type.items() if phrase not in known_phrases
    )

    attributes: dict[str, Any] = {
        "lan": by_type.get(Connection.LAN.phrase, 0),
        "wifi_2_4": by_type.get(Connection.WIFI_2_4.phrase, 0),
        "wifi_5": by_type.get(Connection.WIFI_5_0.phrase, 0),
        "wifi_5_game": by_type.get(Connection.WIFI_5_0_GAME.phrase, 0),
        "guest": by_type.get(Connection.GUEST.phrase, 0),
        "other": other,
        "clients": rows[:_MAX_CLIENT_ROWS],
        "clients_total": total,
        "clients_shown": min(total, _MAX_CLIENT_ROWS),
    }

    return total, attributes


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MiWifi sensor entry.

    :param hass: HomeAssistant: Home Assistant object
    :param config_entry: ConfigEntry: ConfigEntry object
    :param async_add_entities: AddEntitiesCallback: AddEntitiesCallback callback object
    """

    updater: LuciUpdater = async_get_updater(hass, config_entry.entry_id)

    entities: list[MiWifiEntity] = []
    for description in MIWIFI_SENSORS:
        if (
            description.key == ATTR_SENSOR_DEVICES_5_0_GAME
            and not updater.supports_game
        ):
            continue

        if (
            description.key in DISABLE_ZERO
            and updater.data.get(description.key, 0) == 0
        ):
            continue

        if description.key in ONLY_WAN and not updater.supports_wan:
            continue

        entities.append(
            MiWifiSensor(
                f"{config_entry.entry_id}-{description.key}",
                description,
                updater,
            )
        )

    entities.append(
        MiWifiConnectionsSummarySensor(
            f"{config_entry.entry_id}-{ATTR_SENSOR_CONNECTIONS_SUMMARY}",
            updater,
        )
    )

    async_add_entities(entities)


class MiWifiSensor(MiWifiEntity, SensorEntity):
    """MiWifi binary sensor entry."""

    def __init__(
        self,
        unique_id: str,
        description: SensorEntityDescription,
        updater: LuciUpdater,
    ) -> None:
        """Initialize sensor.

        :param unique_id: str: Unique ID
        :param description: SensorEntityDescription: SensorEntityDescription object
        :param updater: LuciUpdater: Luci updater object
        """

        MiWifiEntity.__init__(self, unique_id, description, updater, ENTITY_ID_FORMAT)

        state: Any = self._updater.data.get(description.key, None)
        if state is not None and isinstance(state, Enum):
            state = state.phrase  # type: ignore

        self._attr_native_value = state

    def _handle_coordinator_update(self) -> None:
        """Update state."""

        is_available: bool = self._updater.data.get(ATTR_STATE, False)

        state: Any = self._updater.data.get(self.entity_description.key, None)

        if state is not None and isinstance(state, Enum):
            state = state.phrase  # type: ignore

        if (
            self._attr_native_value == state
            and self._attr_available == is_available  # type: ignore
        ):
            return

        self._attr_available = is_available
        self._attr_native_value = state

        self.async_write_ha_state()


class MiWifiConnectionsSummarySensor(MiWifiEntity, SensorEntity):
    """Sensor: total clients and per-connection breakdown (see attributes)."""

    def __init__(self, unique_id: str, updater: LuciUpdater) -> None:
        """Initialize connections summary sensor."""

        MiWifiEntity.__init__(
            self, unique_id, CONNECTIONS_SUMMARY_DESCRIPTION, updater, ENTITY_ID_FORMAT
        )

        count, attrs = _build_connections_summary(updater)
        self._attr_native_value = count
        self._attr_extra_state_attributes = attrs

    def _handle_coordinator_update(self) -> None:
        """Update state."""

        is_available: bool = self._updater.data.get(ATTR_STATE, False)

        count, attrs = _build_connections_summary(self._updater)

        if (
            self._attr_native_value == count
            and self._attr_available == is_available
            and self._attr_extra_state_attributes == attrs
        ):
            return

        self._attr_available = is_available
        self._attr_native_value = count
        self._attr_extra_state_attributes = attrs

        self.async_write_ha_state()
