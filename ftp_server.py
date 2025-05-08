#!/usr/bin/python3
# secured_ftp_server.py
import socket
import select
import hashlib
import json
import os
import time

# Constants
HOST = '0.0.0.0'
PORT = 2122
ROOT_DIR = './ftp_root'
USER_DB = './users.json'
LOG_FILE = './ftp.log'
HONEYPOT_LOG = './honeypot.log'
MAX_FAILED_ATTEMPTS = 3
SUSPICIOUS_USERS = ['root', 'admin123', 'toor']

# Load user database
def load_users():
    if not os.path.exists(USER_DB):
        return {}
    with open(USER_DB, 'r') as f:
        return json.load(f)

def log_event(message, honeypot=False):
    log_file = HONEYPOT_LOG if honeypot else LOG_FILE
    with open(log_file, 'a') as f:
        f.write(f"[{time.ctime()}] {message}\n")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username, password):
    users = load_users()
    user = users.get(username)
    if user and user['password'] == hash_password(password):
        return user['role']
    return None

# FTP command handling
def list_files(directory):
    return '\n'.join(os.listdir(directory))

def retr_file(directory, filename):
    path = os.path.join(directory, filename)
    if os.path.isfile(path):
        with open(path, 'rb') as f:
            return f.read()
    return None

# Main server
clients = {}
sessions = {}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
server_socket.setblocking(False)

sockets_list = [server_socket]
os.makedirs(ROOT_DIR, exist_ok=True)

print(f"[*] Secure FTP Server running on port {PORT}")

while True:
    read_sockets, _, _ = select.select(sockets_list, [], [])

    for sock in read_sockets:
        if sock == server_socket:
            client_socket, addr = server_socket.accept()
            client_socket.setblocking(False)
            sockets_list.append(client_socket)
            clients[client_socket] = {'stage': 'login', 'username': '', 'failed': 0}
            client_socket.send(b"220 Welcome to SecureFTP. Please login.\nUsername: ")
        else:
            try:
                data = sock.recv(1024)
                if not data:
                    sockets_list.remove(sock)
                    del clients[sock]
                    sock.close()
                    continue

                user_state = clients[sock]
                msg = data.decode().strip()
                print("\'" + msg + "\'", end='')

                # Handle login
                if user_state['stage'] == 'login':
                    user_state['username'] = msg
                    if msg in SUSPICIOUS_USERS:
                        log_event(f"Honeypot triggered by username: {msg}", honeypot=True)
                        sock.send(b"530 Access denied.\n")
                        sockets_list.remove(sock)
                        sock.close()
                        del clients[sock]
                        continue
                    sock.send(b"Password: ")
                    user_state['stage'] = 'password'

                elif user_state['stage'] == 'password':
                    role = authenticate(user_state['username'], msg)
                    if role:
                        log_event(f"User {user_state['username']} authenticated.")
                        sock.send(f"230 Login successful. Role: {role}\nftp> ".encode())
                        user_state['stage'] = 'command'
                        user_state['role'] = role
                        user_state['cwd'] = os.path.join(ROOT_DIR, user_state['username'])
                        os.makedirs(user_state['cwd'], exist_ok=True)
                    else:
                        user_state['failed'] += 1
                        log_event(f"Failed login for {user_state['username']} ({user_state['failed']})")
                        if user_state['failed'] >= MAX_FAILED_ATTEMPTS:
                            sock.send(b"530 Too many failed attempts.\n")
                            sockets_list.remove(sock)
                            sock.close()
                            del clients[sock]
                        else:
                            sock.send(b"Login failed. Username: ")
                            user_state['stage'] = 'login'

                elif user_state['stage'] == 'command':
                    if msg.upper() == 'LIST':
                        files = list_files(user_state['cwd'])
                        sock.send(f"150 Listing:\n{files}\nftp> ".encode())
                    elif msg.upper().startswith('RETR '):
                        filename = msg[5:].strip()
                        filedata = retr_file(user_state['cwd'], filename)
                        if filedata:
                            sock.send(b"150 Opening file\n" + filedata + b"\n226 Transfer complete.\nftp> ")
                        else:
                            sock.send(b"550 File not found.\nftp> ")
                    elif msg.upper() == 'QUIT':
                        sock.send(b"221 Goodbye.\n")
                        sockets_list.remove(sock)
                        sock.close()
                        del clients[sock]
                    else:
                        sock.send(b"502 Command not implemented.\nftp> ")

            except Exception as e:
                print(f"[!] Error: {e}")
                sockets_list.remove(sock)
                sock.close()
                del clients[sock]
