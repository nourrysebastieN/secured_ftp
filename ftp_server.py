#!/usr/bin/python3

import socket
import select
import os

HOST = '0.0.0.0'
PORT = 2122
ROOT_DIR = './ftp_root'

os.makedirs(ROOT_DIR, exist_ok=True)

def list_files():
    return "\n".join(os.listdir(ROOT_DIR))

def retr_file(filename):
    filepath = os.path.join(ROOT_DIR, filename)
    if not os.path.isfile(filepath):
        return None
    with open(filepath, 'rb') as f:
        return f.read()

def handle_client_command(sock, data):
    command = data.strip().split()
    if not command:
        return b'500 Syntax error\r\n'

    cmd = command[0].upper()

    if cmd == 'LIST':
        files = list_files()
        return f"150 Here comes the directory listing:\r\n{files}\r\n226 Directory send OK\r\n".encode()

    elif cmd == 'RETR':
        if len(command) < 2:
            return b'501 Missing filename\r\n'
        filename = command[1]
        filedata = retr_file(filename)
        if filedata is None:
            return b'550 File not found\r\n'
        return b'150 Opening binary mode data connection\r\n' + filedata + b'\r\n226 Transfer complete\r\n'

    elif cmd == 'QUIT':
        return b'221 Goodbye\r\n', True

    else:
        return b'502 Command not implemented\r\n'

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    server_socket.setblocking(False)

    sockets_list = [server_socket]
    clients = {}

    print(f"[*] FTP server started on port {PORT}...")

    while True:
        read_sockets, _, _ = select.select(sockets_list, [], [])

        for sock in read_sockets:
            if sock == server_socket:
                client_socket, client_addr = server_socket.accept()
                print(f"[+] New connection from {client_addr}")
                client_socket.setblocking(False)
                sockets_list.append(client_socket)
                clients[client_socket] = b''
                client_socket.send(b"220 Welcome to SimpleFTP Server\r\n")
            else:
                try:
                    data = sock.recv(1024)
                    if not data:
                        print("[-] Connection closed")
                        sockets_list.remove(sock)
                        sock.close()
                        del clients[sock]
                        continue

                    clients[sock] += data
                    if b'\r\n' in clients[sock]:
                        request = clients[sock].decode().strip()
                        print(f"[>] Received: {request}")
                        response = handle_client_command(sock, request)
                        if isinstance(response, tuple):
                            sock.send(response[0])
                            sockets_list.remove(sock)
                            sock.close()
                            del clients[sock]
                        else:
                            sock.send(response)
                        clients[sock] = b''

                except Exception as e:
                    print(f"[!] Error: {e}")
                    sockets_list.remove(sock)
                    sock.close()
                    del clients[sock]

if __name__ == "__main__":
    main()

