from dataclasses import dataclass
from typing import Optional


@dataclass
class ConnectionState:
	"""Per-client mutable state used by websocket/auth flows."""

	ssid: Optional[str] = None
	check_websocket_if_connect: Optional[int] = None
	ssl_mutual_exclusion: bool = False
	ssl_mutual_exclusion_write: bool = False
	started_listen_instruments: bool = True
	check_rejected_connection: bool = False
	check_accepted_connection: bool = False
	check_websocket_if_error: bool = False
	websocket_error_reason: Optional[str] = None
	balance_id: Optional[int] = None


def create_connection_state() -> ConnectionState:
	return ConnectionState()
