import logging
import socket
import sys
import threading
import time

import actions


class ChatClient:
    HOST = 'localhost'        # The remote host
    PORT = 50001              # The same port as used by the server

    MESSAGE_SIZE = " " * 1024

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self._log = logging.getLogger("ChatClient")
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._read_chat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._read_chat_connected = False

    def __del__(self):
        self.stop_client()

    def start_client(self):
        server_thread = threading.Thread(target=self.handle_server)
        server_thread.start()

        read_chat_thread = threading.Thread(target=self.read_chat)
        read_chat_thread.start()


    def handle_server(self):
        self._socket.connect((self.HOST, self.PORT))
        while True:
            action, msg = self._wait_for_answer(self._socket)
            match action:
                case actions.CHOOSE_USERNAME:
                    self._log.info(msg)
                    chat = input("Select username: ")
                    if chat == "exit":
                        self.send_message(actions.EXIT_SERVER, "")
                        break
                    else:
                        self.send_message(actions.CHOSEN_USERNAME, chat)
                case actions.CHOOSE_CHAT:
                    self._log.info(msg)
                    chat = input("Select chat: ")
                    if chat == "exit":
                        self.send_message(actions.EXIT_SERVER, "")
                        break
                    else:
                        self.send_message(actions.CHOSEN_CHAT, chat)
                case actions.JOIN_CHAT:
                    self._read_chat_socket.connect((self.HOST, self.PORT + 1))
                    self._read_chat_connected = True
                    self._log.info(msg)
                    answer = input("")
                    if answer == "exit":
                        self.exit_chat()
                    else:
                        self.send_message(actions.WRITE_MESSAGE, answer)
                case actions.WAIT_FOR_MESSAGE:
                    answer = input("")
                    if answer == "exit":
                        self.exit_chat()
                    else:
                        self.send_message(actions.WRITE_MESSAGE, answer)
                case _:
                    raise Exception(f"Action '{action}' unknown!")

        self._log.info("Chat closed :)")

    def read_chat(self):
        while True:
            if self._read_chat_connected:
                action, msg = self._wait_for_answer(self._read_chat_socket)
                match action:
                    case actions.FORWARD_MESSAGE:
                        self._log.info(msg)
                    case actions.EXIT_CHAT:
                        self._read_chat_connected = False
                        self._read_chat_socket.close()
                        break
                    case _:
                        raise Exception(f"Action '{action}' unknown!")
            else:
                time.sleep(1)

    def _wait_for_answer(self, socket) -> tuple[str, str]:
        # TODO: Handle this with timeout
        try:
            action = socket.recv(2)
            input = socket.recv(sys.getsizeof(self.MESSAGE_SIZE))
            return action.decode(), input.decode().strip()
        except OSError:
            return actions.EXIT_CHAT, ""

    def send_message(self, action: str, message: str):
        # TODO: Missing check to make sure message is less than 1024 chars
        message = self._fill_message(message)
        # TODO: Does it need extra checks to make sure all data is sent?
        self._socket.sendall(action.encode())
        self._socket.sendall(message.encode())

    def _fill_message(self, message: str) -> str:
        return message + " " * (1024 - len(message))

    def exit_chat(self):
        self.send_message(actions.EXIT_CHAT, "")
        self._read_chat_connected = False
        self._read_chat_socket.close()

    def stop_client(self):
        self._socket.close()


client = ChatClient()
client.start_client()

