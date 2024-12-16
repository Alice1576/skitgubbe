import socket
import pickle

class Network:

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "localhost"
        self.port = 5050
        self.addr = (self.server, self.port)
        self.p = self.connect()

    