from argparse import ArgumentParser, Namespace
from subprocess import Popen
from typing import Optional, Any
import socket
import threading
import sys
import json
import logging

from playsound import playsound # type: ignore

from loggy import setup_logger
import scheduler


PORT = 12799
IP = "127.0.0.1"
ADDR = (IP, PORT)
HEAD_LEN = 32
FORMAT = "utf-8"
DISCONNECT_MESSAGE = {"dcon": True}
STOP_MESSAGE = {"stop": True}

logger: logging.Logger = logging.getLogger()

def play_notif(file:str="notif.mp3") -> None:
    threading.Thread(target=lambda: Popen(f"ffplay {file} -nodisp -autoexit".split())).start()


class Backend:
    pass

class Server:
    def __init__(self: 'Server') -> None:
        self.server: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(ADDR)
        self.open: bool = True
    
    def handle_client(self: 'Server', conn: socket.socket, addr: tuple[str, int]) -> None: 
        logger.info(f"New connection from {addr}")
        connected: bool = True
        while connected:
            head: str = conn.recv(HEAD_LEN).decode(FORMAT)
            if not head:
                break;
            msg_len: int = int(head)
            msg: dict[Any, Any] = json.loads(conn.recv(msg_len).decode(FORMAT))
            logger.info(f"message recieved: {msg}")
            if msg == DISCONNECT_MESSAGE:
                connected = False
                logger.info(f"Disconnecting from {addr}")
                conn.close()
            elif msg == STOP_MESSAGE:
                connected = False
                self.stop()
            else:
                play_notif()

    def start(self: 'Server') -> None:
        self.server.listen()
        logger.info(f"Listening on port {PORT}")
        while self.open:
            conn: socket.socket
            addr: tuple[str, int]
            conn, addr = self.server.accept()
            thread: threading.Thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()

    def stop(self: 'Server') -> None:
        logger.info("Shutting down server")
        self.server.shutdown(socket.SHUT_RDWR)
        self.server.close()
        exit()

class Client:
    def __enter__(self: 'Client') -> 'Client':
        self.client: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(ADDR)
        return self

    def __exit__(self: 'Client', etype: Optional[type], evalue: Optional[Exception], etrace: None) -> None:
        self.send(DISCONNECT_MESSAGE)

    def send(self: 'Client', msg: dict[Any, Any]) -> None:
        sendable: bytes = json.dumps(msg).encode(FORMAT)
        msg_len: bytes = str(len(sendable)).encode(FORMAT)
        msg_len += b' ' * (HEAD_LEN - len(msg_len))
        self.client.send(msg_len)
        self.client.send(sendable)


if __name__ == "__main__":
    parser: ArgumentParser = ArgumentParser()
    subcommand = parser.add_mutually_exclusive_group()
    subcommand.add_argument('--server', action='store_true', help="Start the server")
    subcommand.add_argument('--stop', action='store_true', help="Stop the server")
    parser.add_argument('--verbose', '-v', action='store_true', help="Log more things")
    args: Namespace = parser.parse_args()

    setup_logger(args.verbose)

    if args.server:
        server: Server = Server()
        try:
            server.start()
        except KeyboardInterrupt:
            server.stop()
    else:
        with Client() as client:
            if args.stop:
                client.send(STOP_MESSAGE)
            else:
                client.send({"hello": "world"})
