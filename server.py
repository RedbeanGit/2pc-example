""" Provides a Server class representing the coordinator. """

import socket
import threading

HOST = 'localhost'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

class Server:
    """ This class represents the coordinator. """
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []
        self.started = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_thread = threading.Thread(target=self.accept)

        self.socket.bind((self.host, self.port))
        self.socket.listen()

    def accept(self):
        """ Wait and accept connections from clients in a separated thread. """
        while self.started:
            conn, addr = self.socket.accept()
            print('New connection from', addr)
            self.clients.append(conn)

    def start(self):
        """ Start the server. """
        self.started = True
        self.listen_thread.start()

    def stop(self):
        """ Stop the server. """
        self.started = False
        for client in self.clients:
            client.close()
        self.listen_thread.join()
        self.socket.close()

    def run_transaction(self, query):
        """ Send a transaction to clients. """
        responses = []
        for client in self.clients:
            client.sendall(b'ready?')
            data = client.recv(1024)

            if data:
                responses.append(data.decode())
            else:
                self.clients.remove(client)

        if 'no' in responses:
            print('At least one client is not ready')
            for client in self.clients:
                client.sendall(b'abort')
        else:
            print('All clients are ready')
            responses = []
            for client in self.clients:
                client.sendall(query.encode())
                data = client.recv(1024)

                if data:
                    responses.append(data.decode())
                else:
                    self.clients.remove(client)
            print('Transaction sent')

            if 'fail' in responses:
                for client in self.clients:
                    client.sendall(b'abort')
                print('Transaction aborted')
            else:
                for client in self.clients:
                    client.sendall(b'commit')
                print('Transaction committed')


if __name__ == '__main__':
    server = Server(HOST, PORT)
    server.start()
    print('Server started')
    try:
        while True:
            server.run_transaction(input('Enter a query: '))
    except KeyboardInterrupt:
        server.stop()
