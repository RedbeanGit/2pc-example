""" Provides a Server class representing the coordinator. """

import logging
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
            conn, _ = self.socket.accept()
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

    def send(self, msg):
        """ Send a message to all clients. """
        print('Send', msg)
        for client in self.clients:
            client.sendall(msg.encode())

    def recv(self):
        """ Receive a message from a client. """
        datas = set()
        for client in self.clients:
            data = client.recv(1024)
            if data:
                print('Receive', data.decode())
                datas.add(data.decode())
            else:
                self.clients.remove(client)
        return datas

    def run_transaction(self, query):
        """ Send a transaction to clients. """
        print('INITIAL')
        logging.info('begin_commit')
        self.send(f'PREPARE {query}')

        print('WAIT')

        if 'VOTE-ABORT' in self.recv():
            logging.info('abort')
            self.send('GLOBAL-ABORT')
            print('ABORT')
        else:
            logging.info('commit')
            self.send('GLOBAL-COMMIT')
            print('COMMIT', query)
        self.recv()
        logging.info('end_of_transaction')


if __name__ == '__main__':
    logging.basicConfig(filename='output-coordinator.log')
    server = Server(HOST, PORT)
    server.start()
    try:
        while True:
            server.run_transaction(input('Enter a query: '))
    except KeyboardInterrupt:
        server.stop()
