"""
What do I want this App to do?
    - Server that contains N chats
    - User can access and join any chat they want
"""

import logging
import socket
import threading
from time import sleep

import actions


class ChatServer:
    HOST = 'localhost'
    PORT = 50001

    MESSAGE_SIZE = " " * 1024

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self._log = logging.getLogger("ChatServer")
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket_chats = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._chats = set(["1", "2", "3", "4", "5"])
        self._users = set()
        self._users_in_chat = {chat: {} for chat in self._chats}
        self._count_users = 0

    def __del__(self):
        self.stop_server()

    def start_server(self):
        self._log.info(f"Starting server at {self.HOST}:{self.PORT}")
        self._socket.bind((self.HOST, self.PORT))
        self._socket.listen(3)
        self._socket_chats.bind((self.HOST, self.PORT + 1))
        self._socket_chats.listen(3)
        while True:
            connection, address = self._socket.accept() # Waits for connection
            client_thread = threading.Thread(target=self.handle_client, args=(connection, address))
            client_thread.start()

        # self.stop_server()
        # self._log.info("Server stopped. Exiting.")

    def handle_client(self, connection, address):
        self._log.info(f"Connected by {address}")
        welcome_msg = "Welcome to the Storm Chat! :)\n\n"
        choose_username_msg = "Please choose a username."
        choose_chat_msg = "Select which chat do you want to join:\n"
        choose_chat_msg  += "\n".join([f"\t- {chat}" for chat in self._chats])
        exit_chat_msg = "\n\nType 'exit' to leave a chat or the server."
        self.send_message(connection, actions.CHOOSE_USERNAME, welcome_msg + choose_username_msg + exit_chat_msg)

        current_chat = None
        user_name = None
        while True:
            action, msg = self._wait_for_answer(connection)
            match action:
                case actions.CHOSEN_USERNAME:
                    if msg in self._users:
                        self._log.info(f"User chose username '{msg}'. But it already exists. Asking for another one.")
                        self.send_message(connection, actions.CHOOSE_USERNAME, "Username already in use. Please choose another one.")
                        continue
                    self._log.info(f"User chose username '{msg}'")
                    user_name = msg
                    self._users.add(user_name)
                    self.send_message(connection, actions.CHOOSE_CHAT, choose_chat_msg + exit_chat_msg)
                case actions.CHOSEN_CHAT:
                    if msg not in self._chats:
                        self.send_message(connection, actions.CHOOSE_CHAT, "Chat not available. Please choose another one.")
                        continue
                    self._log.info(f"User {user_name} joined the chat {msg}")
                    current_chat = msg
                    self.send_message(connection, actions.JOIN_CHAT, f"You are now in chat {msg}")
                    chat_conn, _ = self._socket_chats.accept()
                    self._users_in_chat[current_chat][user_name] = chat_conn
                case actions.WRITE_MESSAGE:
                    self._log.info(f"[CHAT {current_chat}] {user_name}: '{msg}'")
                    for user, conn in self._users_in_chat[current_chat].items():
                        if user != user_name:
                            # Probably should be done in parallel, but whatever
                            self.send_message(conn, actions.FORWARD_MESSAGE, f"[{user_name}]: {msg}")
                    self.send_message(connection, actions.WAIT_FOR_MESSAGE, '')
                case actions.EXIT_CHAT:
                    self._log.info(f"User {user_name} exited chat {current_chat}")
                    del self._users_in_chat[current_chat][user_name]
                    self.send_message(connection, actions.CHOOSE_CHAT, welcome_msg + choose_chat_msg + exit_chat_msg)
                case actions.EXIT_SERVER:
                    self._log.info(f"User {user_name} exited the server.")
                    break
                case _:
                    raise Exception(f"Action '{action}' unknown!")

        self._users.remove(user_name)

    def _wait_for_answer(self, connection) -> tuple[str, str]:
        if connection:
            # TODO: Handle this with timeout
            while True:
                action = connection.recv(2)
                input = connection.recv(1024)
                if action != b'' and input != b'': 
                    return action.decode(), input.decode().strip()
                sleep(0.5)
        else:
            raise Exception("Connection not yet initialized!")

    def send_message(self, connection, action: str, message: str):
        # TODO: Missing check to make sure message is less than 1024 chars
        message = self._fill_message(message)
        # TODO: Does it need extra checks to make sure all data is sent?
        connection.sendall(action.encode())
        connection.sendall(message.encode())

    def _fill_message(self, message: str) -> str:
        return message + " " * (1024 - len(message))

    def stop_server(self):
        self._log.info("Stopping server")
        self._socket.close()


server = ChatServer()
server.start_server()

