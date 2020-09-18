# Copyright 2020 TestProject (https://testproject.io)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import socket
import atexit

from urllib.parse import urlparse
from src.testproject.sdk.exceptions import AgentConnectException


class SocketManager:

    __instance = None

    __socket = None

    def __init__(self):
        """Create SocketManager instance and register shutdown hook"""
        atexit.register(self.close_socket)

    @classmethod
    def instance(cls):
        """Return the singleton instance of the SocketManager class"""
        if cls.__instance is None:
            cls.__instance = SocketManager()
        return cls.__instance

    def close_socket(self):
        """Close the connection to the Agent development socket"""
        if self.is_connected():
            logging.debug("Closing socket connection...")

            try:
                self.__socket.shutdown(socket.SHUT_RDWR)
                self.__socket.close()
                self.__socket = None
                logging.info(
                    f"Connection to Agent closed successfully"
                )
            except socket.error as msg:
                logging.error(
                    f"Failed to close socket connection to Agent: {msg}"
                )

    def open_socket(self, socket_address: str, socket_port: int):
        """Opens a connection to the Agent development socket

        Args:
            socket_address (str): The address for the socket
            socket_port (int): The development socket port to connect to
        """
        if self.is_connected():
            logging.debug("Socket is already connected")
            return

        host = urlparse(socket_address).hostname

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.__socket.connect((host, socket_port))

        if not self.is_connected():
            raise AgentConnectException("Failed connecting to Agent socket")

        logging.info(f"Socket connection to {host}:{socket_port} established successfully")

    def is_connected(self) -> bool:
        """Sends a simple message to the socket to see if it's connected

            Returns:
                bool: True if the socket is connected, False otherwise
        """
        try:
            self.__socket.send("test".encode("utf-8"))
            return True
        except socket.error as msg:
            logging.error(f"Socket not connected: {msg}")
            return False
