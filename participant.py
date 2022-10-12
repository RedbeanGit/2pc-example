""" Connect a client and wait for transactions. """

import socket

HOST = 'localhost'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print('Connected to server')

    data = s.recv(1024)
    print('Received', repr(data))

    if data.decode() == 'ready?':
        s.sendall(input('Is this db ready? (yes/no) ').encode())

    data = s.recv(1024)
    print('Received', repr(data))

    if data.decode() == 'abort':
        print('Canceling')

    else:
        print('Starting transaction', data.decode())
        s.sendall(input('Is this transaction successful? (success/fail) ').encode())

        data = s.recv(1024)
        print('Received', repr(data))

        if data.decode() == 'abort':
            print('Aborting transaction')

        elif data.decode() == 'commit':
            print('Committing transaction')
