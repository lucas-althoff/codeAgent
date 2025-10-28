"""PostgreSQL NOTIFY/LISTEN event listener service."""

import asyncio
import json
from typing import Any, Callable

import asyncpg

from src.config import settings


class EventListener:
    """
    PostgreSQL event listener using LISTEN/NOTIFY.

    This service listens to PostgreSQL notifications and executes
    registered callback functions when events occur.
    """

    def __init__(self):
        """Initialize the event listener."""
        self.connection: asyncpg.Connection | None = None
        self.channels: dict[str, list[Callable]] = {}
        self.is_listening = False

    async def connect(self) -> None:
        """Establish connection to PostgreSQL."""
        if self.connection is not None:
            return

        # Parse postgres URL to extract connection parameters
        url = settings.postgres_url
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "")

        auth_and_rest = url.split("@")
        user_pass = auth_and_rest[0].split(":")
        host_port_db = auth_and_rest[1].split("?")[0]
        host_port = host_port_db.split("/")[0]
        database = host_port_db.split("/")[1]
        host = host_port.split(":")[0]
        port = int(host_port.split(":")[1])

        user = user_pass[0]
        password = user_pass[1]

        self.connection = await asyncpg.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database,
        )
        print("[EVENT LISTENER] Connected to PostgreSQL")

    async def disconnect(self) -> None:
        """Close the PostgreSQL connection."""
        if self.connection:
            await self.connection.close()
            self.connection = None
            print("[EVENT LISTENER] Disconnected from PostgreSQL")

    def register_callback(self, channel: str, callback: Callable[[dict], None]) -> None:
        """
        Register a callback function for a specific channel.

        Args:
            channel: The PostgreSQL notification channel to listen to
            callback: Async function to call when notification is received
        """
        if channel not in self.channels:
            self.channels[channel] = []
        self.channels[channel].append(callback)
        print(f"[EVENT LISTENER] Registered callback for channel: {channel}")

    async def start_listening(self) -> None:
        """
        Start listening to registered channels.

        This is a long-running coroutine that should be run in the background.
        """
        if not self.connection:
            await self.connect()

        self.is_listening = True

        # Add listener for each registered channel
        for channel in self.channels.keys():
            await self.connection.add_listener(channel, self._notification_handler)
            print(f"[EVENT LISTENER] Now listening to channel: {channel}")

        print("[EVENT LISTENER] Event listener is running...")

        # Keep the listener alive
        try:
            while self.is_listening:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("[EVENT LISTENER] Listener cancelled")
            await self.stop_listening()

    async def stop_listening(self) -> None:
        """Stop listening to all channels."""
        self.is_listening = False

        if self.connection:
            for channel in self.channels.keys():
                try:
                    await self.connection.remove_listener(
                        channel, self._notification_handler
                    )
                    print(f"[EVENT LISTENER] Stopped listening to channel: {channel}")
                except Exception as e:
                    print(f"[EVENT LISTENER] Error removing listener for {channel}: {e}")

            await self.disconnect()

    def _notification_handler(
        self, connection: asyncpg.Connection, pid: int, channel: str, payload: str
    ) -> None:
        """
        Handle incoming notifications from PostgreSQL.

        Args:
            connection: Database connection
            pid: Process ID that sent the notification
            channel: Channel name
            payload: JSON payload as string
        """
        try:
            # Parse the JSON payload
            data = json.loads(payload)

            print(
                f"[EVENT LISTENER] Received notification on channel '{channel}': "
                f"{data.get('action')} for {data.get('entity_type')}"
            )

            # Execute all registered callbacks for this channel
            if channel in self.channels:
                for callback in self.channels[channel]:
                    try:
                        # If callback is async, schedule it
                        if asyncio.iscoroutinefunction(callback):
                            asyncio.create_task(callback(data))
                        else:
                            callback(data)
                    except Exception as e:
                        print(
                            f"[EVENT LISTENER] Error executing callback for {channel}: {e}"
                        )

        except json.JSONDecodeError as e:
            print(f"[EVENT LISTENER] Failed to parse notification payload: {e}")
        except Exception as e:
            print(f"[EVENT LISTENER] Error handling notification: {e}")


# Global event listener instance
_event_listener: EventListener | None = None


def get_event_listener() -> EventListener:
    """
    Get or create the global event listener instance.

    Returns:
        EventListener instance
    """
    global _event_listener
    if _event_listener is None:
        _event_listener = EventListener()
    return _event_listener


# Example callback functions
async def log_analysis_event(event_data: dict[str, Any]) -> None:
    """
    Example callback for analysis_history events.

    Args:
        event_data: Event payload from PostgreSQL
    """
    action = event_data.get("action")
    entity_id = event_data.get("entity_id")
    print(f"[ANALYSIS EVENT] Analysis {entity_id} was {action}")


async def log_event_creation(event_data: dict[str, Any]) -> None:
    """
    Example callback for events table events.

    Args:
        event_data: Event payload from PostgreSQL
    """
    action = event_data.get("action")
    print(f"[EVENT CREATION] New event logged: {action}")
