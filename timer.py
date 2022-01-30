from argparse import ArgumentParser
import socket
import threading
import logging
import sys
import json
from playsound import playsound

PORT = 2799
IP = "127.0.0.1"
ADDR = (IP, PORT)
HEAD_LEN = 32
FORMAT = "utf-8"
DISCONNECT_MESSAGE = {"dcon": True}

class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(ADDR)
    
    def handle_client(self, conn, addr): 
        logging.info(f"New connection from {addr}")
        connected = True
        while connected:
            head = conn.recv(HEAD_LEN).decode(FORMAT)
            if not head:
                break;
            msg_len = int(head)
            msg = json.loads(conn.recv(msg_len).decode(FORMAT))
            logging.info(f"message recieved: {msg}")
            if msg == DISCONNECT_MESSAGE:
                connected = False
            threading.Thread(target=lambda: playsound("notif.mp3")).start()

        logging.info(f"Disconnecting from {addr}")
        conn.close()

    def start(self):
        self.server.listen()
        logging.info(f"Listening on port {PORT}")
        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()

class Client:
    def __enter__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(ADDR)
        return self

    def __exit__(self, etype, evalue, etrace):
        self.send(DISCONNECT_MESSAGE)

    def send(self, msg):
        sendable = json.dumps(msg).encode(FORMAT)
        msg_len = str(len(sendable)).encode(FORMAT)
        msg_len += b' ' * (HEAD_LEN - len(msg_len))
        self.client.send(msg_len)
        self.client.send(sendable)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--server', action='store_true')
    args = parser.parse_args()

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    #logging.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] - %(message)s"))
    
    if args.server:
        server = Server()
        server.start()
    else:
        with Client() as client:
            pass
