""" Connect a client and wait for transactions. """

import logging
import socket

HOST = 'localhost'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

def ask_input(msg, yes, nope):
    """ Ask for an input. """
    while True:
        answer = input(f'{msg} ({yes}/{nope}) ')
        if answer == yes:
            return True
        if answer == nope:
            return False


def receive(conn):
    data = conn.recv(1024).decode()
    print('Receive', data)
    return data


def send(conn, msg):
    print('Send', msg)
    conn.sendall(msg.encode())

logging.basicConfig(filename='output-participant.log')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    while True:
        try:
            data = receive(s)

            if data.startswith('PREPARE'):
                request = data.split(' ', 1)[1]
                print('INITIAL')

                if ask_input('Ready to commit?', 'yes', 'no'):
                    logging.info('ready')
                    send(s, 'VOTE-COMMIT')
                else:
                    logging.info('abort')
                    send(s, 'VOTE-ABORT')

            print('READY')
            data = receive(s)

            if data == 'GLOBAL-ABORT':
                logging.info('abort')
                print('ABORT')
            elif data == 'GLOBAL-COMMIT':
                logging.info('commit')
                print('COMMIT', request)
            send(s, 'ACK')
        except KeyboardInterrupt:
            print('Closing connection')
            break
