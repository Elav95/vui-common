import traceback

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
import asyncio
import json
import uuid

from vui_common.configs.config_proxy import config_app
from vui_common.logger.logger_proxy import logger
from vui_common.models.user_session import UserSession
from vui_common.security.authentication.tokens import get_user_entity_from_token
from vui_common.ws.ws_message import WebSocketMessage, build_message


class BaseWebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket):
        """Manages the WebSocket connection and authenticates the user only after receiving a valid token."""
        try:
            await websocket.accept()
            user = None         # Initialize the user as None
            auth_timeout = 5    # Maximum time in seconds to authenticate

            while user is None:  # Continue until it receives a valid token
                try:
                    message = await asyncio.wait_for(websocket.receive_text(), timeout=auth_timeout)  # only pings allowed
                    data = json.loads(message) if message.startswith('{') else message
                    if not isinstance(data, dict):
                        logger.error(f"Websocket message is not a dict: {message}")
                        continue

                    data = WebSocketMessage(**data)
                except asyncio.TimeoutError:
                    logger.info("Timeout without authentication. Keeping connection open for pings only.")
                    break  # Exits the authentication loop and only allows ping
                except WebSocketDisconnect as e:
                    if e.code == 1005:
                        logger.warning("Client disconnected without a status code (1005)")
                    else:
                        logger.info(f"WebSocket disconnected with code {e.code}: {e.reason}")
                    return
                except Exception as e:
                    # logger.error(f"WebSocket Receive Error: {e}")
                    await websocket.send_json(build_message(
                        type_="validation_error",
                        kind="error",
                        payload={"error": str(e)}
                    ))
                    traceback.print_exc()
                    # return  # Terminate the connection if there is an error in receiving the message
                    continue

                if data.type == "ping" and data.kind == "request":
                    # Responds to ping to keep the connection open
                    await self.__send_pong(websocket, data)
                    continue  # Continue to receive messages without closing the connection

                # if auth is disabled
                if not config_app.app.auth_enabled:
                    user = UserSession(username="guest", is_guest=True)
                elif data.type == "authentication" and data.kind == "request":
                    # Treats the message as a JWT token
                    user = await get_user_entity_from_token(data.payload.get("token"))

                    #
                    # uncomment to enable session with cookies (no 3/3)
                    #
                    # user = await get_user_entity_from_token(token=websocket.cookies.get("auth_token"))

                if user:
                    self.active_connections[str(user.id)] = websocket
                    response = build_message(
                        type_="authentication",
                        kind="response",
                        payload={"message": 'Connection READY!'}
                    )

                    await self.send_personal_message(str(user.id), json.dumps(response))
                    await self.on_user_authenticated(str(user.id))
                    await self.listen_for_messages(websocket, str(user.id))

                    return  # Ends the loop after authenticating the user

            # If no valid token has been received
            try:
                while True:
                    message = await websocket.receive_text()  # only pings allowed
                    data = json.loads(message) if message.startswith('{') else message
                    if not isinstance(data, dict):
                        logger.error(f"Websocket message is not a dict: {message}")
                        continue

                    data = WebSocketMessage(**data)

                    if data.type == "ping" and data.kind == "request":
                        await self.__send_pong(websocket, data)
                    else:
                        logger.warning("Unauthenticated client tried to send a message. Closing connection.")
                        await websocket.close(1001)
                        return
            except asyncio.TimeoutError:
                logger.info("Closing unauthenticated connection after inactivity.")
                await websocket.close(1001)
            except WebSocketDisconnect:
                logger.info("Unauthenticated WebSocket disconnected.")
            except Exception as e:
                logger.error(f"Error in unauthenticated WebSocket handling: {e}")
                await websocket.close(1001)

        except WebSocketDisconnect:
            logger.debug("WebSocket disconnected")
            await websocket.close(1001)
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            await websocket.close(1001)

    async def disconnect_websocket(self, websocket: WebSocket):
        user_id = None
        for uid, conn in self.active_connections.items():
            if conn == websocket:
                user_id = uid
                break
        if user_id:
            try:
                await websocket.close(code=1001)
            except Exception:
                logger.warning(f"WebSocket for user {user_id} was already closed.")
            finally:
                self.active_connections.pop(user_id, None)
                logger.debug(f"Disconnected user {user_id} and removed from active connections.")

    def disconnect(self, user_id):
        self.active_connections[user_id].close(1001)
        del self.active_connections[user_id]

    async def send_personal_message(self, user_id, message: str):
        try:
            if user_id is not None:
                await self.active_connections[str(user_id)].send_text(message)
        except KeyError:
            logger.warning(f"User ID {user_id} not found in active connections.")
        except AttributeError:
            logger.error(f"Connection object for user ID {user_id} does not support send_text method.")
        except Exception as e:
            logger.error(f"An unexpected error occurred while sending message to user ID {user_id}: {str(e)}")

    async def broadcast(self, message: str):
        for user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message)
            except Exception as Ex:
                logger.error("error", Ex)

    async def __send_pong(self, websocket, data):
        response = build_message(
            type_="pong",
            kind="response",
            request_id=data.request_id
        )
        await websocket.send_json(response)

    async def listen_for_messages(self, websocket: WebSocket, user_id: str):
        """Listen for incoming messages from the client"""
        logger.info(f"Start listen for incoming messages from the client.....")
        try:
            while True:
                message = await websocket.receive_text()
                data = json.loads(message)
                data = WebSocketMessage(**data)

                if data.type == "ping" and data.kind == "request":
                   await self.__send_pong(websocket, data)
                else:
                    try:
                        await self.handle_custom_action(user_id, data, websocket)
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON from {user_id}: {message}")
        except WebSocketDisconnect:
            logger.warning(f"User {user_id} disconnected.")
            await self.disconnect_websocket(websocket)

        except Exception as e:
            logger.error(f"Error in listen_for_messages: {e}")
            await self.disconnect_websocket(websocket)

    # 🔁 Hook: can be overridden by the subclasses
    async def on_user_authenticated(self, user_id: str):
        logger.debug(f"__on_user_authenticated {user_id}")
        pass

    # 🔁 Hook: can be overridden by the subclasses
    async def handle_custom_action(self, user_id: str, data: WebSocketMessage, websocket: WebSocket):
        logger.warning(f"Unhandled action from {user_id}: {data}")
