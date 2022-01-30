from argparse import ArgumentParser
import socket
import threading
import logging
import sys

PORT = 2799
IP = "127.0.0.1"
ADDR = (IP, PORT)
HEADER_LEN = 64

class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(ADDR)
    
    def handle_client(self, conn, addr): 
        logging.info(f"New connection from {addr}")
        connected = True
        while connected:
            msg_len = conn.recv(HEADER_LEN)

    def start(self):
        self.server.listen()
        logging.info(f"Listening on port {PORT}")
        while True:
            con, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()

def run_client():
    pass

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
        pass
